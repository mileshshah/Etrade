# E*TRADE AI Full-Stack Dashboard (Angular)

A full-stack application featuring a FastAPI backend and an Angular frontend to manage your E*TRADE portfolio and get insights from Google Gemini.

## Features

- **Angular Dashboard**: Modern, dark-themed UI for all account activities.
- **Account View**: Real-time cash and net value display.
- **Portfolio Table**: Detailed view of holdings (Symbol, Qty, Cost, Market Value).
- **Interactive Orders**: Preview and place Buy/Sell orders directly from the UI.
- **Gemini AI Chat**: Dedicated sidebar to chat with Gemini about your holdings (privacy-filtered).
- **FastAPI Backend**: Robust API with OAuth 1.0a and Swagger documentation.

## Prerequisites

- Python 3.6+
- Node.js (v18+) and npm
- Angular CLI (`npm install -g @angular/cli`)
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
   Frontend opens at `http://localhost:4200` (default Angular port).

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

## Running with Docker (Recommended)

You can run the entire application (Backend + Frontend) using Docker Compose. This is the easiest way to get started.

### Prerequisites
- Docker and Docker Compose installed.

### Steps
1. **Configure API Keys**: Ensure `config_sandbox.json` or `config_prod.json` are updated with your E*TRADE and Gemini keys.
2. **Start the Application**:
   ```bash
   docker-compose up --build
   ```
3. **Access the Dashboard**:
   Open your browser to [http://localhost](http://localhost).

### Troubleshooting
- The frontend container uses an Nginx proxy to communicate with the backend. Ensure port 80 and 8000 are not already in use on your host.
- If you change the configuration files on your host, you may need to restart the containers (`docker-compose restart backend`).

## AI-Driven Trading

This application now supports AI-driven trading via Gemini. You can instruct Gemini to preview or execute trades for you.

- **Function Calling**: Gemini is equipped with tools to call `preview_etrade_trade` and `place_etrade_trade`.
- **Account Awareness**: Gemini is provided with your current cash balance and holdings to help inform its actions.
- **Manual Confirmation**: While Gemini can call the tools, it's recommended to first ask it to 'preview' a trade so you can see the estimates before it 'places' the order.

**Example Interaction:**
> "Gemini, I have $5000 in cash. Preview a buy of 10 shares of AAPL for me."

Gemini will call the preview tool, report the estimated cost, and then you can say:
> "Looks good, place the order."
