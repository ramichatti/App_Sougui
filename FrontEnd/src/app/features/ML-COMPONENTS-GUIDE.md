# 🎨 ML Components Style Guide & Internationalization

## Overview
This guide outlines the standard styling and translation practices for all Machine Learning components in the Sougui application.

---

## 🌍 Internationalization (i18n)

### Language Support
All ML components support both **French (FR)** and **English (EN)** through the `TranslationService`.

### Adding Translation Keys

1. **Define keys in `translation.service.ts`:**
```typescript
'componentName.key': { 
  fr: 'Texte en français', 
  en: 'Text in English' 
}
```

2. **Use in components:**
```typescript
// In TypeScript
import { TranslationService } from '../../core/services/translation.service';

constructor(public translate: TranslationService) {}

// Use in code
this.translate.translate('componentName.key')
```

3. **Use in templates:**
```html
<!-- In HTML/Template -->
<h1>{{ translate.translate('componentName.title') }}</h1>
```

### Common Translation Keys for ML Components

**Headers:**
- `{component}.title` - Main component title
- `{component}.subtitle` - Component subtitle

**Buttons:**
- `{component}.predict` - "Predict" action
- `{component}.analyze` - "Analyze" action
- `{component}.simulate` - "Simulate" action

**Errors:**
- `common.connectionError` - Connection error message
- `common.selectOption` - Selection required message

**Loading:**
- `{component}.predicting` - Loading state text
- `{component}.analyzing` - Analyzing state text

### Example: Complete Bilingual Component

```typescript
// component.ts
export class MyMLComponent {
  results: any = null;
  isLoading = false;
  
  constructor(public translate: TranslationService) {}
  
  analyze() {
    this.isLoading = true;
    // ... API call ...
    this.isLoading = false;
    this.notif.success(this.translate.translate('myComponent.success'));
  }
}
```

```html
<!-- component.html -->
<div class="ml-header">
  <h1 class="ml-title">{{ translate.translate('myComponent.title') }}</h1>
  <p class="ml-subtitle">{{ translate.translate('myComponent.subtitle') }}</p>
</div>

<button class="ml-btn ml-btn-primary" (click)="analyze()" [disabled]="isLoading">
  <span *ngIf="!isLoading">{{ translate.translate('myComponent.analyze') }}</span>
  <span *ngIf="isLoading">{{ translate.translate('myComponent.analyzing') }}</span>
</button>
```

---

## 🎨 Color Palette

### Blue & White Theme (Primary)

```css
/* Primary Blues */
--ml-blue-900: #1e3a8a   /* Dark blue - Headers, main text */
--ml-blue-800: #1e40af   /* Medium-dark blue */
--ml-blue-700: #1d4ed8
--ml-blue-600: #2563eb
--ml-blue-500: #3b82f6   /* Bright blue - Buttons, icons */
--ml-blue-400: #60a5fa
--ml-blue-300: #93c5fd
--ml-blue-200: #bfdbfe   /* Light blue - Borders */
--ml-blue-100: #dbeafe   /* Lighter blue - Backgrounds */
--ml-blue-50: #eff6ff    /* Almost white - Light backgrounds */

/* Accent Colors */
--ml-green: #16a34a      /* Success - Green cards */
--ml-purple: #7c3aed     /* Info - Purple cards */
--ml-orange: #f59e0b     /* Warning - Orange cards */
--ml-red: #ef4444        /* Error - Red cards */
```

### Usage Examples

```css
/* Headers */
.title { color: var(--ml-blue-900); }

/* Buttons */
.btn-primary { background: linear-gradient(135deg, var(--ml-blue-500), var(--ml-blue-800)); }

/* Borders */
.card { border: 1.5px solid var(--ml-blue-200); }

/* Backgrounds */
.panel { background: var(--ml-blue-50); }
```

---

## 🏗️ Component Structure

### Directory Layout
```
src/app/features/
├── ml-component-name/
│   ├── ml-component-name.component.ts
│   ├── ml-component-name.component.html
│   └── ml-component-name.component.css
├── ml-shared-styles.css
└── ml-components-guide.md (this file)
```

### TypeScript File Template

```typescript
import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../core/services/auth.service';
import { TranslationService } from '../../core/services/translation.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-ml-component',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './ml-component.component.html',
  styleUrls: ['./ml-component.component.css']
})
export class MlComponentComponent implements OnInit {
  isLoading = false;
  errorMessage = '';
  
  constructor(
    private http: HttpClient,
    private authService: AuthService,
    public translate: TranslationService
  ) {}

  ngOnInit(): void {
    // Initialize component
  }

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }
}
```

### HTML Template Structure

```html
<div class="ml-container">
  <div class="ml-content">
    <!-- Header -->
    <div class="ml-header">
      <div class="ml-header-left">
        <div class="ml-header-icon">
          <!-- SVG Icon -->
        </div>
        <div>
          <h1 class="ml-title">{{ translate.translate('component.title') }}</h1>
          <p class="ml-subtitle">{{ translate.translate('component.subtitle') }}</p>
        </div>
      </div>
      <div class="ml-header-badge">ML Algorithm Name</div>
    </div>

    <!-- KPI Cards -->
    <div class="ml-kpi-row">
      <div class="ml-kpi-card blue">
        <div class="ml-kpi-icon"><!-- Icon --></div>
        <div class="ml-kpi-body">
          <div class="ml-kpi-value">0</div>
          <div class="ml-kpi-label">{{ translate.translate('component.metric1') }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="ml-split">
      <!-- Left Panel -->
      <div class="ml-split-left">
        <div class="ml-panel-head">
          <div class="ml-panel-head-left">
            <span class="ml-panel-title">{{ translate.translate('component.select') }}</span>
            <span class="ml-count-chip">Count</span>
          </div>
          <span class="ml-panel-source">SOURCE</span>
        </div>

        <!-- Search -->
        <div class="ml-panel-search" [class.active]="searchTerm.length > 0">
          <input 
            class="ml-panel-search-input"
            type="text"
            [(ngModel)]="searchTerm"
            [placeholder]="translate.translate('component.search')"
          />
        </div>

        <!-- List Content -->
        <div class="list">
          <!-- Items -->
        </div>
      </div>

      <!-- Right Panel -->
      <div class="ml-split-right">
        <!-- Details/Results -->
      </div>
    </div>
  </div>
</div>
```

### CSS Styling Structure

```css
/* Container */
.component-container {
  /* Import shared styles */
}

.component-content {
  /* Shared layout class */
}

/* Custom component-specific styles */
.component-custom-element {
  /* Component-specific styling */
}

/* Responsive */
@media (max-width: 1024px) {
  /* Tablet styles */
}

@media (max-width: 640px) {
  /* Mobile styles */
}
```

---

## 📋 Checklist for New ML Components

- [ ] **Imports:**
  - [ ] CommonModule, FormsModule for directives
  - [ ] TranslationService for i18n
  - [ ] AuthService for authentication
  - [ ] environment for API URLs

- [ ] **Translation Keys:**
  - [ ] Added all text keys to translation.service.ts
  - [ ] Used `translate.translate()` for all user-facing text
  - [ ] Included FR and EN versions for all keys

- [ ] **Styling:**
  - [ ] Used blue/white color palette
  - [ ] Followed component structure template
  - [ ] Responsive design (mobile, tablet, desktop)
  - [ ] Consistent spacing and typography

- [ ] **API Integration:**
  - [ ] Used `environment.apiUrl` for API calls
  - [ ] Proper error handling with translations
  - [ ] Loading states with translated text
  - [ ] Headers include authorization token

- [ ] **User Experience:**
  - [ ] Clear error messages
  - [ ] Loading indicators
  - [ ] Empty states
  - [ ] Proper form validation

---

## 🌐 Current ML Components

| Component | Status | Translations | Styling |
|-----------|--------|--------------|---------|
| Client Segmentation | ✅ Complete | ✅ Full EN/FR | ✅ Blue/White |
| Demand Prediction | ✅ Complete | ✅ Full EN/FR | ✅ Blue/White |
| Price Simulator | ✅ Complete | ✅ Full EN/FR | ✅ Blue/White |
| Best Seller B2C | ✅ Complete | ✅ Full EN/FR | ✅ Blue/White |
| Supplier Classification | ✅ Complete | ✅ Full EN/FR | ✅ Blue/White |
| Distance Analysis | ✅ Updated | ✅ Full EN/FR | ✅ Blue/White |
| Predict Cost | ✅ Updated | ✅ Full EN/FR | ✅ Blue/White |
| ML Security | ✅ Updated | ✅ Full EN/FR | ✅ Blue/White |

---

## 🎯 Best Practices

### 1. **Consistent Terminology**
Use the same translation keys for similar concepts across components:
- Use `common.loading` for all loading states
- Use `common.selectOption` for selection prompts
- Use `common.connectionError` for API errors

### 2. **Error Handling**
Always provide user-friendly error messages:
```typescript
error: (err) => {
  const message = err.error?.error || this.translate.translate('common.connectionError');
  this.errorMessage = message;
  this.notif.error(message);
}
```

### 3. **Loading States**
Show clear feedback during async operations:
```html
<button [disabled]="isLoading">
  <span *ngIf="!isLoading">{{ translate.translate('action.label') }}</span>
  <span *ngIf="isLoading">{{ translate.translate('action.loading') }}</span>
</button>
```

### 4. **Accessibility**
- Use semantic HTML
- Include aria labels for interactive elements
- Maintain sufficient color contrast
- Support keyboard navigation

### 5. **Performance**
- Use OnPush change detection strategy when possible
- Implement pagination for large datasets
- Lazy load non-critical data
- Debounce search inputs

---

## 📞 Support & Questions

For questions about:
- **Translations**: Check `translation.service.ts`
- **Styling**: Reference `ml-shared-styles.css`
- **Components**: Review existing ML components as examples

---

## 📝 Version History

- **v1.0** - Initial ML components style guide
- **May 4, 2026** - Blue/White theme standardization
- **EN/FR** - Full bilingual support