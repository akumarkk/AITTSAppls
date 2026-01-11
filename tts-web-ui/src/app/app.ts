// src/app/app.component.ts
import { Component, signal } from '@angular/core';
import { LocalTtsService } from './services/tts.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="container">
      <h1>Canopy Orpheus TTS</h1>
      <textarea [(ngModel)]="text" placeholder="Enter text here... [cheerful]"></textarea>
      
      <div class="controls">
        <button (click)="speak()" [disabled]="loading()">
          {{ loading() ? 'Generating...' : 'Speak' }}
        </button>
      </div>

      @if (audioUrl()) {
        <audio [src]="audioUrl()" controls autoplay></audio>
      }
    </div>
  `,
  styles: [`
    .container { padding: 20px; max-width: 600px; margin: auto; }
    textarea { width: 100%; height: 100px; margin-bottom: 10px; }
    button { padding: 10px 20px; cursor: pointer; }
  `]
})
export class AppComponent {
  text = 'Hello! [cheerful] This is Canopy Labs Orpheus running in Angular.';
  audioUrl = signal<string | null>(null);
  loading = signal(false);

  constructor(private ttsService: LocalTtsService) {}

  async speak() {
    this.loading.set(true);
    try {
      const audioUrlString = await this.ttsService.getAudio(this.text);
      console.log(`audioUrlString ${audioUrlString}`);
      // const audioUrlString = URL.createObjectURL(blob as Blob);
      this.audioUrl.set(audioUrlString);
    } catch (error) {
      console.error('TTS Error:', error);
      alert('Failed to generate speech.');
    } finally {
      this.loading.set(false);
    }
  }
}