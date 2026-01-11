import torch
import soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from transformers import AutoModelForCausalLM, AutoTokenizer
from snac import SNAC
import os

app = FastAPI()

# Configuration
MODEL_ID = "canopylabs/orpheus-3b-0.1-ft"
SNAC_ID = "hubertsiuzdak/snac_24khz"
SNAC_PATH = r"./snac/snac_24khz"
MODEL_PATH = r"./orpheus-3b-0.1-ft"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 1. Load Tokenizer and Model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH, 
    torch_dtype=torch.bfloat16, 
    device_map="auto",
    local_files_only=True
)

# 2. Load SNAC Audio Decoder
snac_model = SNAC.from_pretrained(SNAC_PATH, local_files_only=True).to(DEVICE).eval()

def reconstruct_snac_codes(flattened_codes):
    """Orpheus outputs 7 tokens per frame. SNAC expects 4 hierarchical layers."""
    # Logic: Layer 1 (1x), Layer 2 (2x), Layer 3 (4x) = 7 tokens per chunk
    codes_l1 = flattened_codes[0::7].unsqueeze(0)       # 1 token
    codes_l2 = flattened_codes[1::7].unsqueeze(0)       # 2 tokens (interleaved)
    codes_l2_alt = flattened_codes[4::7].unsqueeze(0)
    codes_l3 = flattened_codes[2::7].unsqueeze(0)       # 4 tokens (interleaved)
    # ... Simplified reshaping for SNAC 24khz (3-4 layers)
    # Most Orpheus implementations use a specific helper or slicing:
    return [codes_l1, torch.stack([codes_l2, codes_l2_alt], dim=2).flatten(1,2), ...]

@app.post("/generate")
async def generate_tts(text: str, voice: str = "tara"):
    text = data.get("input", "")
    voice = data.get("voice", "tara")
    
    # Orpheus prompt format
    full_prompt = f"{voice}: {text}"
    inputs = tokenizer(full_prompt, return_tensors="pt").to(DEVICE)
    # Orpheus uses a specific prompt format for voices
    # Example: "tara: Hello, how are you today?"
    full_prompt = f"{voice}: {text}"
    
    inputs = tokenizer(full_prompt, return_tensors="pt").to(DEVICE)
    
    with torch.no_grad():
        # Generate audio tokens
        output_tokens = model.generate(
            **inputs, 
            max_new_tokens=1024, 
            do_sample=True, 
            temperature=0.7,
            repetition_penalty=1.1
        )
        
        # Extract only the newly generated audio tokens
        # Note: In Orpheus, audio tokens typically start after a specific offset
        audio_codes = output_tokens[0][inputs.input_ids.shape[-1]:]
        
        # Convert codes to SNAC format (3 layers of codes)
        # This part requires reshaping based on the SNAC layers (usually 1:2:4 ratio)
        # For simplicity, we assume the model output is flattened
        # You may need 'orpheus-speech' helper if raw reshaping fails
        
        # Decode to Audio
        audio_waveform = snac_model.decode(audio_codes)
        
    # Save temporary file
    output_path = "speech.wav"
    sf.write(output_path, audio_waveform.cpu().numpy().squeeze(), 24000)
    
    return FileResponse(output_path, media_type="audio/wav")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7878)