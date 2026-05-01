import {
  Component, signal, ViewChild, ElementRef, AfterViewChecked, HostListener
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GeminiChatService, ChatMessage } from '../../../core/services/gemini-chat.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-chatbot',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css']
})
export class ChatbotComponent implements AfterViewChecked {
  @ViewChild('messagesContainer') messagesContainer!: ElementRef;
  @ViewChild('inputEl') inputEl!: ElementRef;

  isOpen = signal(false);
  isLoading = signal(false);
  inputText = '';

  /** All messages shown in the UI (includes welcome greeting) */
  messages = signal<ChatMessage[]>([]);

  /**
   * Only actual user↔model turns (excludes the welcome greeting).
   * This is what we send to the Gemini API so the first role is always 'user'.
   */
  private conversationHistory: ChatMessage[] = [];

  private shouldScroll = false;

  readonly suggestions = [
    'Comment accéder à mes dashboards ?',
    'Comment fonctionne la gestion des rôles ?',
    'Que signifie un privilège ?',
    'Comment contacter l\'administrateur ?'
  ];

  constructor(
    private gemini: GeminiChatService,
    public authService: AuthService
  ) {}

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  toggleChat(): void {
    this.isOpen.update(v => !v);
    if (this.isOpen() && this.messages().length === 0) {
      this.addWelcome();
    }
    if (this.isOpen()) {
      setTimeout(() => this.inputEl?.nativeElement?.focus(), 100);
    }
  }

  closeChat(): void { this.isOpen.set(false); }

  @HostListener('document:keydown.escape')
  onEscape(): void { if (this.isOpen()) this.closeChat(); }

  send(): void {
    const text = this.inputText.trim();
    if (!text || this.isLoading()) return;

    const userMsg: ChatMessage = { role: 'user', text, timestamp: new Date() };

    // Add to UI
    this.messages.update(m => [...m, userMsg]);
    this.inputText = '';
    this.isLoading.set(true);
    this.shouldScroll = true;

    // Snapshot of conversation history BEFORE adding the new user msg
    // (sendMessage will append it internally)
    const historySnapshot = [...this.conversationHistory];

    this.gemini.sendMessage(historySnapshot, text).subscribe({
      next: (reply) => {
        const modelMsg: ChatMessage = { role: 'model', text: reply, timestamp: new Date() };

        // Persist both turns in conversation history for the API
        this.conversationHistory.push(userMsg, modelMsg);

        this.messages.update(m => [...m, modelMsg]);
        this.isLoading.set(false);
        this.shouldScroll = true;
      },
      error: (err: Error) => {
        let errorText = 'Désolé, une erreur est survenue. Veuillez réessayer.';
        if (err.message === 'QUOTA') {
          errorText = 'Le service est temporairement surchargé. Attendez quelques secondes et réessayez.';
        }
        const errMsg: ChatMessage = { role: 'model', text: errorText, timestamp: new Date() };
        this.messages.update(m => [...m, errMsg]);
        this.isLoading.set(false);
        this.shouldScroll = true;
      }
    });
  }

  sendSuggestion(text: string): void {
    this.inputText = text;
    this.send();
  }

  clearChat(): void {
    this.conversationHistory = [];
    this.messages.set([]);
    this.addWelcome();
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.send();
    }
  }

  formatTime(date: Date): string {
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  }

  formatText(text: string): string {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  }

  private addWelcome(): void {
    const user = this.authService.currentUser();
    const name = user ? ` ${user.first_name}` : '';
    const welcome: ChatMessage = {
      role: 'model',
      text: `Bonjour${name} ! Je suis l'assistant IA de Sougui. Comment puis-je vous aider aujourd'hui ?`,
      timestamp: new Date()
    };
    // Only in UI — NOT in conversationHistory (so the first API turn starts with 'user')
    this.messages.set([welcome]);
    this.shouldScroll = true;
  }

  private scrollToBottom(): void {
    try {
      const el = this.messagesContainer?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    } catch {}
  }
}
