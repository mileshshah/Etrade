from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import os
import json

from .etrade_auth import ETradeAuth
from .etrade_client import ETradeClient
from .gemini_client import GeminiClient

app = FastAPI(title="E*TRADE API Service")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory state management
class AppState:
    def __init__(self):
        self.auth: Optional[ETradeAuth] = None
        self.client: Optional[ETradeClient] = None
        self.gemini: Optional[GeminiClient] = None
        self.env: str = "sandbox"
        self.gemini_api_key: Optional[str] = None

state = AppState()

class AuthRequest(BaseModel):
    env: str = "sandbox"

class VerifierRequest(BaseModel):
    verifier: str

class OrderPreviewRequest(BaseModel):
    accountIdKey: str
    symbol: str
    orderAction: str
    quantity: int
    priceType: str = "MARKET"

class OrderPlaceRequest(BaseModel):
    accountIdKey: str
    previewId: int
    symbol: str
    orderAction: str
    quantity: int
    priceType: str = "MARKET"

class ChatRequest(BaseModel):
    accountIdKey: str
    message: str

@app.get("/status")
def get_status():
    return {
        "authenticated": state.client is not None,
        "env": state.env
    }

@app.post("/auth/initialize")
def initialize_auth(req: AuthRequest):
    state.env = req.env
    config_file = f"config_{state.env}.json"
    if not os.path.exists(config_file):
        raise HTTPException(status_code=404, detail=f"Config file {config_file} not found")

    state.auth = ETradeAuth(config_file)
    url = state.auth.get_authorization_url()
    return {"authorization_url": url}

@app.post("/auth/verify")
def verify_auth(req: VerifierRequest):
    if not state.auth:
        raise HTTPException(status_code=400, detail="Auth not initialized")

    try:
        credentials = state.auth.get_access_token(req.verifier)
        state.client = ETradeClient(credentials)
        state.gemini_api_key = credentials.get("gemini_api_key")
        return {"status": "success", "message": "Successfully authenticated with E*TRADE"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/accounts")
def list_accounts():
    if not state.client:
        raise HTTPException(status_code=401, detail="Not authenticated")

    accounts = state.client.list_accounts()
    if not accounts:
        return {"accounts": []}
    return {"accounts": accounts}

@app.get("/accounts/{account_id_key}/balance")
def get_balance(account_id_key: str):
    if not state.client:
        raise HTTPException(status_code=401, detail="Not authenticated")

    balance = state.client.get_account_balances(account_id_key)
    return {"balance": balance}

@app.get("/portfolio/{account_id_key}")
def get_portfolio(account_id_key: str):
    if not state.client:
        raise HTTPException(status_code=401, detail="Not authenticated")

    portfolio = state.client.view_portfolio(account_id_key)
    return {"portfolio": portfolio}

@app.post("/order/preview")
def preview_order(req: OrderPreviewRequest):
    if not state.client:
        raise HTTPException(status_code=401, detail="Not authenticated")

    preview = state.client.preview_order(
        req.accountIdKey, req.symbol, req.orderAction, req.quantity, req.priceType
    )
    if not preview:
        raise HTTPException(status_code=400, detail="Order preview failed")

    return preview

@app.post("/order/place")
def place_order(req: OrderPlaceRequest):
    if not state.client:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = state.client.place_order(
        req.accountIdKey, req.previewId, req.symbol, req.orderAction, req.quantity, req.priceType
    )
    if not result:
        raise HTTPException(status_code=400, detail="Order placement failed")

    return result

@app.post("/gemini/chat")
def chat_portfolio(req: ChatRequest):
    if not state.client:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not state.gemini:
        if not state.gemini_api_key:
             raise HTTPException(status_code=400, detail="Gemini API Key missing")
        state.gemini = GeminiClient(state.gemini_api_key)

    portfolio_response = state.client.view_portfolio(req.accountIdKey)
    if not portfolio_response:
        raise HTTPException(status_code=404, detail="Portfolio not found or empty")

    # Filter data for Gemini privacy: Only symbol, company, and quantity
    filtered_data = []
    try:
        portfolio_data = portfolio_response.get('PortfolioResponse', {}).get('AccountPortfolio', [])
        if portfolio_data:
            positions = portfolio_data[0].get('Position', [])
            for pos in positions:
                filtered_data.append({
                    "symbol": pos.get('Product', {}).get('symbol'),
                    "company": pos.get('symbolDescription'),
                    "quantity": pos.get('quantity')
                })
    except (IndexError, AttributeError):
        pass

    if not filtered_data:
        raise HTTPException(status_code=404, detail="No positions found in portfolio to analyze")

    response = state.gemini.chat(filtered_data, req.message)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
