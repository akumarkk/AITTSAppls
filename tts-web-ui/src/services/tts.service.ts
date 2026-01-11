// src/app/services/local-tts.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class LocalTtsService {
  // Use /api/v1 because of our proxy configuration
  private apiUrl = '/api/v1/audio/speech';

  constructor(private http: HttpClient) {}

  async speak(text: string, voice: string = 'tara'): Promise<string> {
    const body = {
      model: "orpheus",
      input: text,
      voice: voice,
      response_format: "wav"
    };

    const blob = await firstValueFrom(
      this.http.post(this.apiUrl, body, { responseType: 'blob' })
    );

    // Create a local URL for the audio player
    return URL.createObjectURL(blob);
  }
}