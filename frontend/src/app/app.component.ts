import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from './api.service';
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

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    LucideAngularModule
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: [
    // This is often done in the module, but for standalone:
    { provide: 'LucideIcons', useValue: { Briefcase, LayoutDashboard, Send, ShoppingCart, User, RefreshCw, MessageSquare } }
  ]
})
export class AppComponent implements OnInit {
  // Icons for template usage
  readonly Briefcase = 'Briefcase';
  readonly LayoutDashboard = 'LayoutDashboard';
  readonly Send = 'Send';
  readonly ShoppingCart = 'ShoppingCart';
  readonly User = 'User';
  readonly RefreshCw = 'RefreshCw';
  readonly MessageSquare = 'MessageSquare';

  authStatus = { authenticated: false, env: 'sandbox' };
  loading = true;
  error: string | null = null;
  accounts: any[] = [];
  selectedAccount: any = null;
  portfolio: any[] = [];
  balances: any = null;
  messages: any[] = [];
  chatInput = '';
  chatLoading = false;

  authUrl = '';
  verifier = '';

  // Order form states
  order = { symbol: '', action: 'BUY', quantity: 1, priceType: 'MARKET' };
  preview: any = null;
  orderLoading = false;

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.checkStatus();
  }

  checkStatus() {
    this.api.getStatus().subscribe({
      next: (data) => {
        this.authStatus = data;
        if (data.authenticated) {
          this.fetchAccounts();
        }
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Backend service not reachable';
        this.loading = false;
      }
    });
  }

  fetchAccounts() {
    this.api.getAccounts().subscribe({
      next: (data) => {
        const accountList = data.accounts.AccountListResponse?.Accounts?.Account || [];
        this.accounts = accountList;
        if (accountList.length > 0 && !this.selectedAccount) {
          this.handleSelectAccount(accountList[0]);
        }
      },
      error: () => this.error = 'Failed to fetch accounts'
    });
  }

  handleSelectAccount(acc: any) {
    this.selectedAccount = acc;
    this.api.getBalance(acc.accountIdKey).subscribe(res => {
      this.balances = res.balance.BalanceResponse;
    });
    this.api.getPortfolio(acc.accountIdKey).subscribe(res => {
      this.portfolio = res.portfolio.PortfolioResponse?.AccountPortfolio?.[0]?.Position || [];
    });
  }

  onAccountChange(event: any) {
    const acc = this.accounts.find(a => a.accountId === event.target.value);
    if (acc) this.handleSelectAccount(acc);
  }

  handleInitialize(env: string) {
    this.api.initializeAuth(env).subscribe({
      next: (data) => this.authUrl = data.authorization_url,
      error: () => this.error = 'Failed to initialize auth'
    });
  }

  handleVerify() {
    this.api.verifyAuth(this.verifier).subscribe({
      next: () => this.checkStatus(),
      error: () => this.error = 'Verification failed'
    });
  }

  handleSendMessage(event: Event) {
    event.preventDefault();
    if (!this.chatInput.trim() || !this.selectedAccount) return;

    const userMsg = { role: 'user', content: this.chatInput };
    this.messages.push(userMsg);
    const currentInput = this.chatInput;
    this.chatInput = '';
    this.chatLoading = true;

    this.api.chatGemini({
      accountIdKey: this.selectedAccount.accountIdKey,
      message: currentInput
    }).subscribe({
      next: (data) => {
        this.messages.push({ role: 'gemini', content: data.response });
        this.chatLoading = false;
      },
      error: () => {
        this.messages.push({ role: 'error', content: 'Chat failed' });
        this.chatLoading = false;
      }
    });
  }

  handlePreview(event: Event) {
    event.preventDefault();
    this.orderLoading = true;
    this.api.previewOrder({
      accountIdKey: this.selectedAccount.accountIdKey,
      symbol: this.order.symbol.toUpperCase(),
      orderAction: this.order.action,
      quantity: this.order.quantity,
      priceType: this.order.priceType
    }).subscribe({
      next: (data) => {
        this.preview = data.PreviewOrderResponse;
        this.orderLoading = false;
      },
      error: () => {
        alert('Preview failed');
        this.orderLoading = false;
      }
    });
  }

  handlePlace() {
    this.orderLoading = true;
    const previewId = this.preview.PreviewIds[0].previewId;
    this.api.placeOrder({
      accountIdKey: this.selectedAccount.accountIdKey,
      previewId: previewId,
      symbol: this.order.symbol.toUpperCase(),
      orderAction: this.order.action,
      quantity: this.order.quantity,
      priceType: this.order.priceType
    }).subscribe({
      next: () => {
        alert('Order placed successfully!');
        this.preview = null;
        this.order = { symbol: '', action: 'BUY', quantity: 1, priceType: 'MARKET' };
        this.handleSelectAccount(this.selectedAccount);
        this.orderLoading = false;
      },
      error: () => {
        alert('Order placement failed');
        this.orderLoading = false;
      }
    });
  }

  cancelOrder() {
    this.preview = null;
  }
}
