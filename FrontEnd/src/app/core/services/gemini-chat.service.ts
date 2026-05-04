import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

export interface ChatMessage {
  role: 'user' | 'model';
  text: string;
  timestamp: Date;
}

interface GeminiPart { text: string; }
interface GeminiContent { role: string; parts: GeminiPart[]; }
interface GeminiResponse {
  candidates: { content: { parts: GeminiPart[] } }[];
}

@Injectable({ providedIn: 'root' })
export class GeminiChatService {
  private readonly apiKey = 'AIzaSyBIzCJaKyWVMX7xHuV49WdcYlfSkpJ8yCc';
  // Use v1 (stable), gemini-2.0-flash
  private readonly apiUrl =
    `https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key=${this.apiKey}`;

  private readonly systemPrompt =
    `Tu es l'assistant IA de Sougui, une plateforme décisionnelle (Business Intelligence) pour les produits artisanaux tunisiens.
Tu aides les utilisateurs à comprendre leurs tableaux de bord Power BI, interpréter les données, et naviguer sur la plateforme.
Réponds en français par défaut, sauf si l'utilisateur écrit en anglais.
Sois concis, professionnel et utile.
Contexte :
- Sougui permet de visualiser des dashboards Power BI selon les rôles et privilèges des utilisateurs.
- Les rôles incluent Administrateur, Directeur Vente, Directeur Achat, etc.
- Les admins gèrent les utilisateurs, rôles, privilèges et dashboards Power BI.
- Les notifications informent les utilisateurs des nouveaux accès accordés.`;

  constructor(private http: HttpClient) {}

  /**
   * Send a message to Gemini.
   * `conversationHistory` must contain only actual user↔model turns
   * (NOT the welcome greeting — it would make the first content role = "model",
   *  which Gemini rejects).
   */
  sendMessage(conversationHistory: ChatMessage[], userText: string): Observable<string> {
    // Build contents: prior turns + new user turn
    const contents: GeminiContent[] = [
      ...conversationHistory.map(m => ({
        role: m.role,
        parts: [{ text: m.text }]
      })),
      { role: 'user', parts: [{ text: userText }] }
    ];

    const body = {
      system_instruction: { parts: [{ text: this.systemPrompt }] },
      contents
    };

    return this.http.post<GeminiResponse>(this.apiUrl, body).pipe(
      map(res => {
        const text = res?.candidates?.[0]?.content?.parts?.[0]?.text;
        if (!text) throw new Error('Empty response from Gemini');
        return text;
      }),
      catchError(err => {
        console.error('Gemini API error:', err);
        const status = err?.status ?? 0;
        const msg: string = err?.error?.error?.message ?? '';
        if (status === 429) {
          return throwError(() => new Error('QUOTA'));
        }
        if (status === 400) {
          return throwError(() => new Error('BAD_REQUEST: ' + msg));
        }
        return throwError(() => new Error(msg || 'UNKNOWN'));
      })
    );
  }
}
