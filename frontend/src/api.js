import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  getStatus: () => client.get('/status'),
  initializeAuth: (env) => client.post('/auth/initialize', { env }),
  verifyAuth: (verifier) => client.post('/auth/verify', { verifier }),
  getAccounts: () => client.get('/accounts'),
  getBalance: (id) => client.get(`/accounts/${id}/balance`),
  getPortfolio: (id) => client.get(`/portfolio/${id}`),
  previewOrder: (data) => client.post('/order/preview', data),
  placeOrder: (data) => client.post('/order/place', data),
  chatGemini: (data) => client.post('/gemini/chat', data),
};
