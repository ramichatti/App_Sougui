import { Component } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { NotificationComponent } from './shared/components/notification/notification.component';
import { NavbarComponent } from './shared/components/navbar/navbar.component';
import { ChatbotComponent } from './shared/components/chatbot/chatbot.component';
import { CommonModule } from '@angular/common';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NotificationComponent, NavbarComponent, ChatbotComponent, CommonModule],
  template: `
    <app-notification></app-notification>
    @if (showNavbar) {
      <app-navbar></app-navbar>
    }
    <router-outlet></router-outlet>
    @if (showChatbot) {
      <app-chatbot></app-chatbot>
    }
  `
})
export class AppComponent {
  title = 'Sougui';
  showNavbar = false;
  showChatbot = false;

  constructor(private router: Router) {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      const url = event.url;
      const isAuthPage = url.includes('/login') || url.includes('/forgot-password');
      this.showNavbar = !isAuthPage;
      this.showChatbot = !isAuthPage;
    });
  }
}
