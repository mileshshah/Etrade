import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = '';

  constructor(private http: HttpClient) {}

  getStatus(): Observable<any> {
    return this.http.get(`${this.baseUrl}/status`);
  }

  initializeAuth(env: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/initialize`, { env });
  }

  verifyAuth(verifier: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/verify`, { verifier });
  }

  getAccounts(): Observable<any> {
    return this.http.get(`${this.baseUrl}/accounts`);
  }

  getBalance(id: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/accounts/${id}/balance`);
  }

  getPortfolio(id: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/portfolio/${id}`);
  }

  previewOrder(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/order/preview`, data);
  }

  placeOrder(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/order/place`, data);
  }

  chatGemini(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/gemini/chat`, data);
  }
}
