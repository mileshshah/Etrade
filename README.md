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

### Windows / Docker Desktop Issues
If you see errors related to `open //./pipe/dockerDesktopLinuxEngine`, this usually means Docker Desktop is not running or the Docker context is incorrect.
- Ensure Docker Desktop is open and the Docker engine has started.
- Try running `docker ps` in your terminal to verify connection.
- If on Windows, ensure you are using a terminal that supports Linux paths (e.g., PowerShell or Git Bash) or use WSL2.

### ⚠️ Common Docker Desktop (Windows) Errors
If you see: `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.`

This indicates that your terminal cannot communicate with the Docker engine. To fix:
1. **Start Docker Desktop**: Ensure the Docker icon is in your system tray and is green (Running).
2. **Check WSL2 Settings**: Go to Docker Desktop Settings > General and ensure "Use the WSL 2 based engine" is checked.
3. **Verify Context**: Run `docker context ls` in your terminal. If `default` is not selected (asterisk next to it), run `docker context use default`.
4. **Test Connection**: Run `docker ps`. If it fails with the same error, your terminal context is not set correctly. Try restarting your terminal (PowerShell or Command Prompt).
5. **Admin Rights**: Sometimes Docker requires the terminal to be run as an Administrator.
