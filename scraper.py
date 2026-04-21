import os
import json
import math
from datetime import datetime

import yfinance as yf

STOCKS = {
    "AAPL": "Apple Inc.",
    "GOOGL": "Alphabet Inc.",
    "MSFT": "Microsoft Corp.",
    "AMZN": "Amazon.com, Inc.",
    "NVDA": "NVIDIA Corporation",
    "AMD": "Advanced Micro Devices, Inc.",
    "MU": "Micron Technology, Inc.",
}

COMPANY_NAMES = STOCKS  # backward-compat alias


def _safe(value, default=None):
    if value is None:
        return default
    try:
        if math.isnan(float(value)):
            return default
    except (TypeError, ValueError):
        pass
    return value


def _pct_return(hist, trading_days: int):
    if hist is None or len(hist) < 2:
        return None
    now_price = hist["Close"].iloc[-1]
    idx = max(0, len(hist) - trading_days - 1)
    past_price = hist["Close"].iloc[idx]
    if not past_price or past_price == 0:
        return None
    return round((now_price - past_price) / past_price * 100, 2)


def _ytd_return(hist):
    if hist is None or hist.empty:
        return None
    current_year = datetime.now().year
    ytd = hist[hist.index.year == current_year]
    if ytd.empty:
        return None
    now_price = hist["Close"].iloc[-1]
    start_price = ytd["Close"].iloc[0]
    if not start_price or start_price == 0:
        return None
    return round((now_price - start_price) / start_price * 100, 2)


def get_stock_data(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)
    info = ticker.info
    hist = ticker.history(period="5y")

    price = _safe(info.get("currentPrice") or info.get("regularMarketPrice"), 0.0)
    prev_close = _safe(
        info.get("previousClose") or info.get("regularMarketPreviousClose"), 0.0
    )
    change = round(price - prev_close, 2) if price and prev_close else 0.0
    change_pct = round(change / prev_close * 100, 2) if prev_close else 0.0

    earnings_date = None
    try:
        cal = ticker.calendar
        if isinstance(cal, dict):
            ed = cal.get("Earnings Date")
            if ed:
                first = ed[0] if isinstance(ed, list) else ed
                earnings_date = (
                    str(first.date()) if hasattr(first, "date") else str(first)
                )
        elif cal is not None and hasattr(cal, "get"):
            ed = cal.get("Earnings Date")
            if ed is not None and len(ed) > 0:
                earnings_date = (
                    str(ed.iloc[0].date())
                    if hasattr(ed.iloc[0], "date")
                    else str(ed.iloc[0])
                )
    except Exception:
        pass

    div_date = None
    try:
        ex_div = info.get("exDividendDate")
        if ex_div:
            div_date = datetime.fromtimestamp(int(ex_div)).strftime("%Y-%m-%d")
    except Exception:
        pass

    last_split = None
    try:
        splits = ticker.splits
        if splits is not None and not splits.empty:
            ratio = splits.iloc[-1]
            last_split = f"{ratio:.0f}:1 on {splits.index[-1].strftime('%Y-%m-%d')}"
    except Exception:
        pass

    return {
        "symbol": symbol,
        "name": STOCKS.get(symbol, symbol),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        # Price / Trading
        "price": price,
        "change": change,
        "change_percent": change_pct,
        "open": _safe(info.get("open") or info.get("regularMarketOpen")),
        "high": _safe(info.get("dayHigh") or info.get("regularMarketDayHigh")),
        "low": _safe(info.get("dayLow") or info.get("regularMarketDayLow")),
        "prev_close": _safe(prev_close),
        "week_52_high": _safe(info.get("fiftyTwoWeekHigh")),
        "week_52_low": _safe(info.get("fiftyTwoWeekLow")),
        "avg_volume": _safe(info.get("averageVolume")),
        "shares_outstanding": _safe(info.get("sharesOutstanding")),
        "market_cap": _safe(info.get("marketCap")),
        "beta": _safe(info.get("beta")),
        # Valuation
        "eps_ttm": _safe(info.get("trailingEps")),
        "pe_ttm": _safe(info.get("trailingPE")),
        "forward_pe": _safe(info.get("forwardPE")),
        "price_to_sales": _safe(info.get("priceToSalesTrailing12Months")),
        "ev_ebitda": _safe(info.get("enterpriseToEbitda")),
        # Profitability
        "revenue_ttm": _safe(info.get("totalRevenue")),
        "ebitda": _safe(info.get("ebitda")),
        "gross_margin": _safe(info.get("grossMargins")),
        "net_margin": _safe(info.get("profitMargins")),
        "roe": _safe(info.get("returnOnEquity")),
        "roic": _safe(info.get("returnOnAssets")),
        # Balance Sheet
        "debt_to_equity": _safe(info.get("debtToEquity")),
        "cash": _safe(info.get("totalCash")),
        "free_cash_flow": _safe(info.get("freeCashflow")),
        # Events
        "earnings_date": earnings_date,
        "dividend_date": div_date,
        "last_split": last_split,
        # Performance Returns
        "return_5d": _pct_return(hist, 5),
        "return_1m": _pct_return(hist, 21),
        "return_3m": _pct_return(hist, 63),
        "return_ytd": _ytd_return(hist),
        "return_1y": _pct_return(hist, 252),
        "return_5y": _pct_return(hist, 1260),
    }


# ── Formatting helpers ────────────────────────────────────────────────────────

def _fp(v):
    return f"${v:,.2f}" if v is not None else "—"


def _fn(v, d=2):
    return f"{v:.{d}f}" if v is not None else "—"


def _fl(v):
    if v is None:
        return "—"
    av = abs(v)
    if av >= 1e12:
        return f"${v/1e12:.2f}T"
    if av >= 1e9:
        return f"${v/1e9:.2f}B"
    if av >= 1e6:
        return f"${v/1e6:.2f}M"
    return f"${v:,.0f}"


def _ret_cell(label: str, val):
    if val is None:
        return f'<div class="detail-item"><div class="detail-label">{label}</div><div class="detail-value">—</div></div>'
    sign = "+" if val >= 0 else ""
    cls = "positive" if val >= 0 else "negative"
    return f'<div class="detail-item"><div class="detail-label">{label}</div><div class="detail-value {cls}">{sign}{val:.1f}%</div></div>'


# ── HTML generation ───────────────────────────────────────────────────────────

def generate_html(stocks: list) -> str:
    cards = ""
    stocks_json = json.dumps(
        [
            {
                "symbol": s.get("symbol"),
                "name": s.get("name"),
                "price": s.get("price", 0),
                "change_percent": s.get("change_percent", 0),
                "change": s.get("change", 0),
            }
            for s in stocks
        ]
    )

    for s in stocks:
        chg = s.get("change") or 0
        chg_pct = s.get("change_percent") or 0
        sign = "+" if chg >= 0 else ""
        cls = "positive" if chg >= 0 else "negative"

        cards += f"""
        <div class="stock-card">
            <div class="stock-header">
                <div>
                    <div class="stock-symbol">{s.get("symbol","")}</div>
                    <div class="stock-name">{s.get("name","")}</div>
                </div>
                <div>
                    <div class="stock-price">{_fp(s.get("price"))}</div>
                    <div class="stock-change {cls}">{sign}{chg:.2f} ({sign}{chg_pct:.2f}%)</div>
                </div>
            </div>
            <div class="stock-details">
                <div class="detail-item"><div class="detail-label">Open</div><div class="detail-value">{_fp(s.get("open"))}</div></div>
                <div class="detail-item"><div class="detail-label">High</div><div class="detail-value">{_fp(s.get("high"))}</div></div>
                <div class="detail-item"><div class="detail-label">Low</div><div class="detail-value">{_fp(s.get("low"))}</div></div>
                <div class="detail-item"><div class="detail-label">Mkt Cap</div><div class="detail-value">{_fl(s.get("market_cap"))}</div></div>
                <div class="detail-item"><div class="detail-label">P/E</div><div class="detail-value">{_fn(s.get("pe_ttm"))}</div></div>
                <div class="detail-item"><div class="detail-label">Beta</div><div class="detail-value">{_fn(s.get("beta"))}</div></div>
                {_ret_cell("5D", s.get("return_5d"))}
                {_ret_cell("1M", s.get("return_1m"))}
                {_ret_cell("1Y", s.get("return_1y"))}
            </div>
        </div>"""

    page_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Stock Tracker</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f0f0f; color: #e5e5e5; min-height: 100vh; padding: 40px 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        header {{ margin-bottom: 40px; }}
        h1 {{ font-size: 28px; font-weight: 600; color: #fff; margin-bottom: 8px; }}
        .subtitle {{ color: #737373; font-size: 14px; }}
        .stock-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }}
        .stock-card {{ background: #171717; border: 1px solid #262626; border-radius: 12px; padding: 20px; transition: border-color 0.2s; }}
        .stock-card:hover {{ border-color: #404040; }}
        .stock-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }}
        .stock-symbol {{ font-size: 18px; font-weight: 600; color: #fff; }}
        .stock-name {{ font-size: 13px; color: #737373; margin-top: 2px; }}
        .stock-price {{ font-size: 22px; font-weight: 600; color: #fff; text-align: right; }}
        .stock-change {{ font-size: 13px; font-weight: 500; margin-top: 4px; text-align: right; }}
        .positive {{ color: #22c55e; }}
        .negative {{ color: #ef4444; }}
        .stock-details {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; padding-top: 14px; border-top: 1px solid #262626; }}
        .detail-item {{ text-align: center; }}
        .detail-label {{ font-size: 10px; color: #525252; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 3px; }}
        .detail-value {{ font-size: 13px; font-weight: 500; color: #a3a3a3; }}
        .agent-panel {{ background: #151515; border: 1px solid #292929; border-radius: 12px; padding: 24px; margin-top: 32px; }}
        .agent-header {{ margin-bottom: 16px; }}
        .agent-title {{ font-size: 18px; font-weight: 600; color: #fff; }}
        .agent-subtitle {{ font-size: 13px; color: #737373; margin-top: 4px; }}
        .quick-prompts {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }}
        .quick-btn {{ padding: 6px 12px; border: 1px solid #333; border-radius: 20px; background: transparent; color: #a3a3a3; font-size: 12px; cursor: pointer; transition: all 0.15s; }}
        .quick-btn:hover {{ border-color: #2563eb; color: #60a5fa; }}
        .chat-history {{ display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; max-height: 500px; overflow-y: auto; min-height: 80px; padding-right: 4px; }}
        .bubble {{ padding: 14px 16px; border-radius: 12px; font-size: 14px; line-height: 1.7; }}
        .bubble.user {{ background: #1e3a5f; border: 1px solid #2563eb; color: #e0f0ff; align-self: flex-end; max-width: 80%; border-radius: 12px 12px 4px 12px; }}
        .bubble.assistant {{ background: #1f1f1f; border: 1px solid #373737; color: #e5e5e5; }}
        .bubble.assistant h1,.bubble.assistant h2,.bubble.assistant h3 {{ color: #fff; margin: 10px 0 5px; font-size: 15px; }}
        .bubble.assistant ul,.bubble.assistant ol {{ padding-left: 18px; margin: 6px 0; }}
        .bubble.assistant li {{ margin: 3px 0; }}
        .bubble.assistant blockquote {{ border-left: 3px solid #404040; padding-left: 12px; color: #737373; margin: 8px 0; font-style: italic; }}
        .bubble.assistant strong {{ color: #fff; }}
        .bubble.assistant p {{ margin: 5px 0; }}
        .bubble.assistant hr {{ border: none; border-top: 1px solid #333; margin: 10px 0; }}
        .bubble.error {{ background: #2d0f0f; border: 1px solid #7f1d1d; color: #fca5a5; }}
        .bubble.loading {{ background: #111; border: 1px dashed #404040; color: #737373; font-style: italic; }}
        .input-row {{ display: grid; grid-template-columns: 1fr auto; gap: 12px; }}
        .agent-input {{ width: 100%; padding: 12px 14px; border-radius: 10px; border: 1px solid #262626; background: #101010; color: #f5f5f5; font-size: 14px; }}
        .agent-input:focus {{ outline: none; border-color: #2563eb; }}
        .send-btn {{ padding: 12px 20px; border: none; border-radius: 10px; background: #2563eb; color: #fff; font-weight: 600; cursor: pointer; transition: background 0.15s; white-space: nowrap; }}
        .send-btn:hover {{ background: #1d4ed8; }}
        .send-btn:disabled {{ background: #1e3a5f; cursor: not-allowed; }}
        .footer {{ text-align: center; margin-top: 32px; font-size: 12px; color: #525252; }}
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>Stock Tracker</h1>
        <p class="subtitle">Real-time market data &middot; AI-powered analysis</p>
    </header>
    <div class="stock-grid">{cards}</div>
    <div class="agent-panel">
        <div class="agent-header">
            <div class="agent-title">Investment Agent</div>
            <div class="agent-subtitle">AI-powered analysis using live scraped financial data</div>
        </div>
        <div class="quick-prompts">
            <button class="quick-btn" onclick="askQuick('Is NVDA overvalued right now?')">Is NVDA overvalued?</button>
            <button class="quick-btn" onclick="askQuick('Compare AAPL vs MSFT long term.')">AAPL vs MSFT</button>
            <button class="quick-btn" onclick="askQuick('Which stock has the strongest balance sheet?')">Best balance sheet?</button>
            <button class="quick-btn" onclick="askQuick('Compare NVDA vs AMD in AI chips.')">NVDA vs AMD (AI)</button>
            <button class="quick-btn" onclick="askQuick('Rank these companies by growth potential.')">Growth ranking</button>
            <button class="quick-btn" onclick="askQuick('Which stock looks safest in a recession?')">Recession safe?</button>
            <button class="quick-btn" onclick="askQuick('Which stock has stronger margins: AMD or MU?')">AMD vs MU margins</button>
            <button class="quick-btn" onclick="askQuick('Best stock to buy for $1000 today?')">Best for $1000?</button>
        </div>
        <div id="chat-history" class="chat-history">
            <div class="bubble loading">Ask me anything about these stocks — I&rsquo;ll use live financial data and AI to answer.</div>
        </div>
        <div class="input-row">
            <input id="agent-query" class="agent-input" type="text" placeholder="Ask me what to invest in..." />
            <button id="send-btn" class="send-btn" type="button">Ask</button>
        </div>
    </div>
    <div class="footer">
        <div>Last updated: {page_ts}</div>
        <div style="margin-top:6px;font-size:11px;color:#404040;">Educational analysis only &mdash; not financial advice.</div>
    </div>
</div>
<script>
const stocksData = {stocks_json};

function appendBubble(cls, content, isText) {{
    const h = document.getElementById('chat-history');
    const b = document.createElement('div');
    b.className = 'bubble ' + cls;
    if (isText) b.textContent = content;
    else b.innerHTML = content;
    h.appendChild(b);
    h.scrollTop = h.scrollHeight;
    return b;
}}

function clearPlaceholder() {{
    const el = document.querySelector('#chat-history .loading');
    if (el) el.remove();
}}

async function sendQuestion(question) {{
    if (!question) return;
    clearPlaceholder();
    appendBubble('user', question, true);
    const loading = appendBubble('loading', 'Analyzing with live data\u2026', true);
    const btn = document.getElementById('send-btn');
    btn.disabled = true;
    document.getElementById('agent-query').value = '';

    try {{
        const resp = await fetch('/api/chat', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{question, tickers: stocksData.map(s => s.symbol)}})
        }});
        loading.remove();
        if (!resp.ok) {{
            const err = await resp.json().catch(() => ({{}}));
            appendBubble('error', 'Error: ' + (err.error || resp.statusText), true);
        }} else {{
            const data = await resp.json();
            const html = typeof marked !== 'undefined'
                ? marked.parse(data.answer)
                : data.answer.replace(/\\n/g, '<br>');
            appendBubble('assistant', html, false);
        }}
    }} catch (e) {{
        loading.remove();
        appendBubble('error', 'Could not reach the AI backend. Run \u201cpython app.py\u201d to enable AI analysis.', true);
    }} finally {{
        btn.disabled = false;
    }}
}}

function askQuick(q) {{
    document.getElementById('agent-query').value = q;
    sendQuestion(q);
}}

document.getElementById('send-btn').addEventListener('click', () => {{
    sendQuestion(document.getElementById('agent-query').value.trim());
}});
document.getElementById('agent-query').addEventListener('keyup', e => {{
    if (e.key === 'Enter') sendQuestion(document.getElementById('agent-query').value.trim());
}});
</script>
</body>
</html>"""


def main():
    symbols = list(STOCKS.keys())
    stocks = []
    for symbol in symbols:
        data = get_stock_data(symbol)
        stocks.append(data)
        print(f"Fetched {symbol}: ${data['price']}")

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w") as f:
        f.write(generate_html(stocks))
    print("Generated docs/index.html")


if __name__ == "__main__":
    main()
