import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { provideHttpClient } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { importProvidersFrom } from '@angular/core';
import {
  LucideAngularModule,
  Briefcase,
  LayoutDashboard,
  Send,
  ShoppingCart,
  User,
  RefreshCw,
  MessageSquare
} from 'lucide-angular';

bootstrapApplication(AppComponent, {
  providers: [
    provideHttpClient(),
    provideAnimations(),
    importProvidersFrom(
      LucideAngularModule.pick({
        Briefcase,
        LayoutDashboard,
        Send,
        ShoppingCart,
        User,
        RefreshCw,
        MessageSquare
      })
    )
  ]
}).catch((err) => console.error(err));
