import React, { useState, useEffect } from 'react';
import { api } from './api';
import { Briefcase, LayoutDashboard, Send, ShoppingCart, User, RefreshCw, MessageSquare } from 'lucide-react';
import './App.css';

function App() {
  const [authStatus, setAuthStatus] = useState({ authenticated: false, env: 'sandbox' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [portfolio, setPortfolio] = useState([]);
  const [balances, setBalances] = useState(null);
  const [messages, setMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  const [authUrl, setAuthUrl] = useState('');
  const [verifier, setVerifier] = useState('');

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      const { data } = await api.getStatus();
      setAuthStatus(data);
      if (data.authenticated) {
        fetchAccounts();
      }
    } catch (err) {
      setError('Backend service not reachable');
    } finally {
      setLoading(false);
    }
  };

  const fetchAccounts = async () => {
    try {
      const { data } = await api.getAccounts();
      const accountList = data.accounts.AccountListResponse?.Accounts?.Account || [];
      setAccounts(accountList);
      if (accountList.length > 0 && !selectedAccount) {
        handleSelectAccount(accountList[0]);
      }
    } catch (err) {
      setError('Failed to fetch accounts');
    }
  };

  const handleSelectAccount = async (acc) => {
    setSelectedAccount(acc);
    try {
      const [balRes, portRes] = await Promise.all([
        api.getBalance(acc.accountIdKey),
        api.getPortfolio(acc.accountIdKey)
      ]);
      setBalances(balRes.data.balance.BalanceResponse);
      const positions = portRes.data.portfolio.PortfolioResponse?.AccountPortfolio?.[0]?.Position || [];
      setPortfolio(positions);
    } catch (err) {
      console.error('Error fetching account details', err);
    }
  };

  const handleInitialize = async (env) => {
    try {
      const { data } = await api.initializeAuth(env);
      setAuthUrl(data.authorization_url);
    } catch (err) {
      setError('Failed to initialize auth');
    }
  };

  const handleVerify = async () => {
    try {
      await api.verifyAuth(verifier);
      checkStatus();
    } catch (err) {
      setError('Verification failed');
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || !selectedAccount) return;

    const userMsg = { role: 'user', content: chatInput };
    setMessages(prev => [...prev, userMsg]);
    setChatInput('');
    setChatLoading(true);

    try {
      const { data } = await api.chatGemini({
        accountIdKey: selectedAccount.accountIdKey,
        message: chatInput
      });
      setMessages(prev => [...prev, { role: 'gemini', content: data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'error', content: 'Chat failed' }]);
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) return <div className="loading-screen">Connecting to E*TRADE Service...</div>;

  if (!authStatus.authenticated) {
    return (
      <div className="auth-container">
        <h1>E*TRADE AI Dashboard</h1>
        {!authUrl ? (
          <div className="auth-step">
            <p>Select environment to begin:</p>
            <button onClick={() => handleInitialize('sandbox')}>Sandbox</button>
            <button onClick={() => handleInitialize('prod')}>Production</button>
          </div>
        ) : (
          <div className="auth-step">
            <p>Step 1: Authorize the application</p>
            <a href={authUrl} target="_blank" rel="noreferrer" className="btn-link">Open Authorization URL</a>
            <p>Step 2: Enter verifier code</p>
            <input
              type="text"
              placeholder="Verifier Code"
              value={verifier}
              onChange={e => setVerifier(e.target.value)}
            />
            <button onClick={handleVerify}>Complete Authentication</button>
          </div>
        )}
        {error && <p className="error">{error}</p>}
      </div>
    );
  }

  return (
    <div className="app-layout">
      <header>
        <div className="logo"><Briefcase size={24} /> <span>E*TRADE AI</span></div>
        <div className="account-selector">
          <RefreshCw onClick={fetchAccounts} className="refresh-icon" size={18} />
          <select value={selectedAccount?.accountId || ''} onChange={(e) => {
            const acc = accounts.find(a => a.accountId === e.target.value);
            handleSelectAccount(acc);
          }}>
            {accounts.map(acc => (
              <option key={acc.accountId} value={acc.accountId}>
                {acc.accountName} ({acc.accountId})
              </option>
            ))}
          </select>
        </div>
      </header>

      <main>
        <div className="main-content">
          <section className="info-grid">
            <div className="card balance-card">
              <h3><User size={18} /> Account Info</h3>
              {balances && (
                <div className="balance-info">
                  <div className="stat">
                    <span>Cash Available</span>
                    <strong>${balances.Computed?.cashAvailableForInvestment?.toLocaleString()}</strong>
                  </div>
                  <div className="stat">
                    <span>Net Value</span>
                    <strong>${balances.Computed?.netAccountValue?.toLocaleString()}</strong>
                  </div>
                </div>
              )}
            </div>

            <div className="card order-card">
              <h3><ShoppingCart size={18} /> Place Order</h3>
              <OrderForm accountIdKey={selectedAccount?.accountIdKey} onOrderSuccess={() => handleSelectAccount(selectedAccount)} />
            </div>
          </section>

          <section className="card portfolio-card">
            <h3><LayoutDashboard size={18} /> Portfolio Holdings</h3>
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Company</th>
                  <th>Quantity</th>
                  <th>Price Paid</th>
                  <th>Market Value</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.map((pos, i) => (
                  <tr key={i}>
                    <td>{pos.Product.symbol}</td>
                    <td>{pos.symbolDescription}</td>
                    <td>{pos.quantity}</td>
                    <td>${pos.pricePaid?.toFixed(2)}</td>
                    <td>${pos.marketValue?.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>

        <aside className="chat-panel">
          <div className="chat-header">
            <h3><MessageSquare size={18} /> Gemini AI Analyst</h3>
          </div>
          <div className="messages">
            {messages.map((m, i) => (
              <div key={i} className={`message ${m.role}`}>
                <div className="content">{m.content}</div>
              </div>
            ))}
            {chatLoading && <div className="message gemini loading">Thinking...</div>}
          </div>
          <form onSubmit={handleSendMessage} className="chat-input">
            <input
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              placeholder="Ask Gemini about your holdings..."
            />
            <button type="submit"><Send size={18} /></button>
          </form>
        </aside>
      </main>
    </div>
  );
}

function OrderForm({ accountIdKey, onOrderSuccess }) {
  const [order, setOrder] = useState({ symbol: '', action: 'BUY', quantity: 1, priceType: 'MARKET' });
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);

  const handlePreview = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.previewOrder({
        accountIdKey,
        symbol: order.symbol.toUpperCase(),
        orderAction: order.action,
        quantity: parseInt(order.quantity),
        priceType: order.priceType
      });
      setPreview(data.PreviewOrderResponse);
    } catch (err) {
      alert('Preview failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePlace = async () => {
    setLoading(true);
    try {
      const previewId = preview.PreviewIds[0].previewId;
      await api.placeOrder({
        accountIdKey,
        previewId,
        symbol: order.symbol.toUpperCase(),
        orderAction: order.action,
        quantity: parseInt(order.quantity),
        priceType: order.priceType
      });
      alert('Order placed successfully!');
      setPreview(null);
      setOrder({ symbol: '', action: 'BUY', quantity: 1, priceType: 'MARKET' });
      onOrderSuccess();
    } catch (err) {
      alert('Order placement failed');
    } finally {
      setLoading(false);
    }
  };

  if (preview) {
    const instr = preview.Order[0].Instrument[0];
    return (
      <div className="order-preview">
        <h4>Confirm Order</h4>
        <p>{instr.orderAction} {instr.quantity} {instr.Product.symbol}</p>
        <p>Est. Total: ${preview.Order[0].estimatedTotalAmount}</p>
        <div className="btn-group">
          <button onClick={handlePlace} disabled={loading}>Confirm</button>
          <button onClick={() => setPreview(null)} className="secondary">Cancel</button>
        </div>
      </div>
    );
  }

  return (
    <form className="order-form" onSubmit={handlePreview}>
      <div className="form-group">
        <input
          placeholder="Symbol"
          value={order.symbol}
          onChange={e => setOrder({...order, symbol: e.target.value})}
          required
        />
        <select value={order.action} onChange={e => setOrder({...order, action: e.target.value})}>
          <option value="BUY">BUY</option>
          <option value="SELL">SELL</option>
        </select>
      </div>
      <div className="form-group">
        <input
          type="number"
          min="1"
          value={order.quantity}
          onChange={e => setOrder({...order, quantity: e.target.value})}
        />
        <select value={order.priceType} onChange={e => setOrder({...order, priceType: e.target.value})}>
          <option value="MARKET">MARKET</option>
          <option value="LIMIT">LIMIT</option>
        </select>
      </div>
      <button type="submit" disabled={loading}>Preview Order</button>
    </form>
  );
}

export default App;
