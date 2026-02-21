# E*TRADE AI Full-Stack Dashboard

A full-stack application featuring a FastAPI backend and a React frontend to manage your E*TRADE portfolio and get insights from Google Gemini.

## Features

- **React Dashboard**: Modern, dark-themed UI for all account activities.
- **Account View**: Real-time cash and net value display.
- **Portfolio Table**: Detailed view of holdings (Symbol, Qty, Cost, Market Value).
- **Interactive Orders**: Preview and place Buy/Sell orders directly from the UI.
- **Gemini AI Chat**: Dedicated sidebar to chat with Gemini about your holdings (privacy-filtered).
- **FastAPI Backend**: Robust API with OAuth 1.0a and Swagger documentation.

## Prerequisites

- Python 3.6+
- Node.js (v18+) and npm
- E*TRADE API keys
- Google Gemini API key

## Installation & Setup

1. **Backend Setup**:
   ```bash
   pip install -r requirements.txt
   ```
   Update `config_sandbox.json` or `config_prod.json` with your keys.

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

You need to run both the backend and frontend simultaneously.

1. **Start Backend**:
   ```bash
   uvicorn api.server:app --reload
   ```
   Backend runs at `http://localhost:8000`. Swagger docs at `/docs`.

2. **Start Frontend**:
   ```bash
   cd frontend
   npm start
   ```
   Frontend opens at `http://localhost:3000`.

## UI Overview

- **Auth Screen**: If not authenticated, you'll be prompted to choose an environment (Sandbox/Prod), visit the E*TRADE auth URL, and enter your verifier code.
- **Header**: Displays the application name and an account selector.
- **Left/Center Panels**:
  - **Account Info**: Displays current cash and net value.
  - **Place Order**: Form to preview and execute stock trades.
  - **Portfolio**: Table showing current holdings.
- **Right Panel**: **Gemini AI Analyst** chatbot.

## Data Privacy

Only `symbol`, `company description`, and `quantity` are shared with Gemini. Sensitive financial values are strictly filtered out by the backend before reaching the AI.
