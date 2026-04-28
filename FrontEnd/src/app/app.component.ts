import { Component } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { NotificationComponent } from './shared/components/notification/notification.component';
import { NavbarComponent } from './shared/components/navbar/navbar.component';
import { CommonModule } from '@angular/common';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NotificationComponent, NavbarComponent, CommonModule],
  template: `
    <app-notification></app-notification>
    @if (showNavbar) {
      <app-navbar></app-navbar>
    }
    <router-outlet></router-outlet>
  `
})
export class AppComponent {
  title = 'Sougui';
  showNavbar = false;

  constructor(private router: Router) {
    // Hide navbar on login and forgot-password pages
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      const url = event.url;
      this.showNavbar = !url.includes('/login') && !url.includes('/forgot-password');
    });
  }
}
