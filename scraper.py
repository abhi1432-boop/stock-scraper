import requests
import os
from datetime import datetime

COMPANY_NAMES = {
    "AAPL": "Apple Inc.",
    "GOOGL": "Alphabet Inc.",
    "MSFT": "Microsoft Corp.",
    "AMZN": "Amazon.com, Inc.",
    "NVDA": "NVIDIA Corporation",
    "AMD": "Advanced Micro Devices, Inc.",
    "MU": "Micron Technology, Inc."
}


def get_stock_data(symbol):
    # fetch stock data from yahoo finance for a given stock symbol
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    result = data["chart"]["result"][0]
    meta = result["meta"]

    price = meta.get("regularMarketPrice", 0.0)
    previous_close = meta.get("chartPreviousClose", 0.0)
    change = round(price - previous_close, 2)
    change_percent = round(meta.get("regularMarketChangePercent", 0.0), 2)
    open_price = meta.get("regularMarketOpen", 0.0)
    high_price = meta.get("regularMarketDayHigh", 0.0)
    low_price = meta.get("regularMarketDayLow", 0.0)

    return {
        "symbol": symbol,
        "name": COMPANY_NAMES.get(symbol, symbol),
        "price": price,
        "change": change,
        "change_percent": change_percent,
        "open": open_price,
        "high": high_price,
        "low": low_price,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def generate_html(stocks):
    cards = ""
    stocks_data = [
        {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "price": stock["price"],
            "change_percent": stock["change_percent"],
            "change": stock["change"]
        }
        for stock in stocks
    ]
    for stock in stocks:
        change_sign = "+" if stock["change"] >= 0 else ""
        percent_sign = "+" if stock["change_percent"] >= 0 else ""
        change_class = "positive" if stock["change"] >= 0 else "negative"

        cards += f"""
            <div class=\"stock-card\">
                <div class=\"stock-header\">
                    <div>
                        <div class=\"stock-symbol\">{stock["symbol"]}</div>
                        <div class=\"stock-name\">{stock["name"]}</div>
                    </div>
                    <div>
                        <div class=\"stock-price\">${stock["price"]:.2f}</div>
                        <div class=\"stock-change {change_class}\">{change_sign}{stock["change"]:.2f} ({percent_sign}{stock["change_percent"]:.2f}%)</div>
                    </div>
                </div>
                <div class=\"stock-details\">
                    <div class=\"detail-item\">
                        <div class=\"detail-label\">Open</div>
                        <div class=\"detail-value\">${stock["open"]:.2f}</div>
                    </div>
                    <div class=\"detail-item\">
                        <div class=\"detail-label\">High</div>
                        <div class=\"detail-value\">${stock["high"]:.2f}</div>
                    </div>
                    <div class=\"detail-item\">
                        <div class=\"detail-label\">Low</div>
                        <div class=\"detail-value\">${stock["low"]:.2f}</div>
                    </div>
                </div>
            </div>
        """

    page_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
        <title>Stock Tracker</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: #0f0f0f;
                color: #e5e5e5;
                min-height: 100vh;
                padding: 40px 20px;
            }}

            .container {{
                max-width: 1000px;
                margin: 0 auto;
            }}

            header {{
                margin-bottom: 40px;
            }}

            h1 {{
                font-size: 28px;
                font-weight: 600;
                color: #fff;
                margin-bottom: 8px;
            }}

            .subtitle {{
                color: #737373;
                font-size: 14px;
            }}

            .stock-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 16px;
            }}

            .stock-card {{
                background: #171717;
                border: 1px solid #262626;
                border-radius: 12px;
                padding: 20px;
                transition: border-color 0.2s ease;
            }}

            .stock-card:hover {{
                border-color: #404040;
            }}

            .stock-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 16px;
            }}

            .stock-symbol {{
                font-size: 18px;
                font-weight: 600;
                color: #fff;
            }}

            .stock-name {{
                font-size: 13px;
                color: #737373;
                margin-top: 2px;
            }}

            .stock-price {{
                font-size: 24px;
                font-weight: 600;
                color: #fff;
                text-align: right;
            }}

            .stock-change {{
                font-size: 14px;
                font-weight: 500;
                margin-top: 4px;
                text-align: right;
            }}

            .stock-change.positive {{
                color: #22c55e;
            }}

            .stock-change.negative {{
                color: #ef4444;
            }}

            .stock-details {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 12px;
                padding-top: 16px;
                border-top: 1px solid #262626;
            }}

            .detail-item {{
                text-align: center;
            }}

            .detail-label {{
                font-size: 11px;
                color: #525252;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 4px;
            }}

            .detail-value {{
                font-size: 14px;
                font-weight: 500;
                color: #a3a3a3;
            }}

            .agent-panel {{
                background: #151515;
                border: 1px solid #292929;
                border-radius: 12px;
                padding: 24px;
                margin-top: 32px;
            }}

            .agent-header {{
                display: flex;
                justify-content: space-between;
                align-items: baseline;
                margin-bottom: 16px;
            }}

            .agent-title {{
                font-size: 18px;
                font-weight: 600;
                color: #fff;
            }}

            .agent-subtitle {{
                font-size: 13px;
                color: #737373;
            }}

            .agent-input-row {{
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 12px;
                margin-bottom: 16px;
            }}

            .agent-input {{
                width: 100%;
                padding: 12px 14px;
                border-radius: 10px;
                border: 1px solid #262626;
                background: #101010;
                color: #f5f5f5;
                font-size: 14px;
            }}

            .agent-button {{
                padding: 12px 18px;
                border: none;
                border-radius: 10px;
                background: #2563eb;
                color: #fff;
                font-weight: 600;
                cursor: pointer;
            }}

            .agent-button:hover {{
                background: #1d4ed8;
            }}

            .agent-response {{
                display: grid;
                gap: 10px;
                min-height: 90px;
            }}

            .agent-bubble {{
                max-width: 100%;
                padding: 14px 16px;
                border-radius: 18px;
                background: #1f1f1f;
                color: #e5e5e5;
                font-size: 14px;
                line-height: 1.7;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
            }}

            .agent-bubble.assistant {{
                border: 1px solid #373737;
            }}

            .agent-bubble.thought {{
                border: 1px dashed #4b5563;
                background: #111111;
                color: #a3a3a3;
                font-style: italic;
            }}

            .agent-bubble strong {{
                color: #fff;
            }}

            .updated {{
                text-align: center;
                margin-top: 32px;
                font-size: 12px;
                color: #525252;
            }}
        </style>
    </head>
    <body>
        <div class=\"container\">
            <header>
                <h1>Stock Tracker</h1>
                <p class=\"subtitle\">Real-time market data</p>
            </header>
            <div class=\"stock-grid\">
                {cards}
            </div>
            <div class="agent-panel">
                <div class="agent-header">
                    <div>
                        <div class="agent-title">Investment Agent</div>
                        <div class="agent-subtitle">Ask which stock you should consider investing in.</div>
                    </div>
                </div>
                <div class="agent-input-row">
                    <input id="agent-query" class="agent-input" type="text" placeholder="Ask me what to invest in..." />
                    <button id="agent-submit" class="agent-button" type="button">Ask</button>
                </div>
                <div id="agent-response" class="agent-response">
                    <div class="agent-bubble thought">Thinking through the latest market data... visualize the strongest themes.</div>
                    <div class="agent-bubble assistant"><strong>Tip:</strong> Try asking a question like "What is the best stock to invest in for 2026?"</div>
                </div>
            </div>
            <p class="updated">Last updated: {page_timestamp}</p>
        </div>
        <script>
            const stocks = {stocks_data};

            function findTopPerformers() {{
                const sorted = stocks.slice().sort((a, b) => b.change_percent - a.change_percent);
                return sorted.slice(0, 3);
            }}

            function findValuePicks() {{
                const sorted = stocks.slice().sort((a, b) => a.price - b.price);
                return sorted.slice(0, 3);
            }}

            function renderAgentResponse(bubbles) {{
                const container = document.getElementById('agent-response');
                container.innerHTML = '';
                bubbles.forEach(bubble => {{
                    const node = document.createElement('div');
                    node.className = 'agent-bubble ' + bubble.type;
                    node.textContent = bubble.text;
                    container.appendChild(node);
                }});
            }}

            function buildAnalysis(items, reason) {{
                if (!items.length) {{
                    return [
                        {{ type: 'thought', text: 'Reviewing available symbols...'}},
                        {{ type: 'assistant', text: 'I do not have enough data to make a strong suggestion right now.'}}
                    ];
                }}

                const summary = items.map(item => item.symbol + ' (' + item.name + ')').join(', ');
                return [
                    {{ type: 'thought', text: 'Analyzing the latest market moves and momentum across the current universe.'}},
                    {{ type: 'assistant', text: 'After reviewing the data, the strongest candidates are ' + summary + '.' }},
                    {{ type: 'assistant', text: 'I recommend these because they best match the requested focus: ' + reason + '.' }}
                ];
            }}

            function handleAgentQuery(query) {{
                const prompt = query.toLowerCase();
                if (prompt.includes('clear cut winner') || prompt.includes('best stock') || prompt.includes('one stock') || prompt.includes('winner')) {{
                    const picks = findTopPerformers();
                    return buildAnalysis(picks, 'the clearest momentum leaders in the current market');
                }}
                if (prompt.includes('growth') || prompt.includes('top') || prompt.includes('strong')) {{
                    const picks = findTopPerformers();
                    return buildAnalysis(picks, 'top growth and momentum names');
                }}
                if (prompt.includes('cheap') || prompt.includes('value') || prompt.includes('low')) {{
                    const picks = findValuePicks();
                    return buildAnalysis(picks, 'lower-priced stocks that could offer value');
                }}
                if (prompt.includes('long') || prompt.includes('hold') || prompt.includes('safe')) {{
                    const picks = stocks.filter(item => ['AAPL', 'MSFT', 'GOOGL'].includes(item.symbol));
                    return buildAnalysis(picks, 'longer-term, more stable large-cap technology names');
                }}
                const picks = findTopPerformers();
                return [
                    {{ type: 'thought', text: 'I am synthesizing the most relevant market signals and relative strength.'}},
                    {{ type: 'assistant', text: 'Based on current data, these names look strongest: ' + picks.map(item => item.symbol + ' (' + item.name + ')').join(', ') + '.' }},
                    {{ type: 'assistant', text: 'Use this as a data-informed starting point rather than a final decision.' }}
                ];
            }}

            document.getElementById('agent-submit').addEventListener('click', () => {{
                const query = document.getElementById('agent-query').value.trim();
                if (!query) {{
                    renderAgentResponse([
                        {{ type: 'thought', text: 'Waiting for your question...'}},
                        {{ type: 'assistant', text: 'Please enter a question about investing to get a recommendation.' }}
                    ]);
                    return;
                }}

                renderAgentResponse([
                    {{ type: 'thought', text: 'Thinking through the market data...'}}
                ]);

                setTimeout(() => {{
                    const bubbles = handleAgentQuery(query);
                    renderAgentResponse(bubbles);
                }}, 500);
            }});

            document.getElementById('agent-query').addEventListener('keyup', (event) => {{
                if (event.key === 'Enter') {{
                    document.getElementById('agent-submit').click();
                }}
            }});
        </script>
    </body>
    </html>
    """


def main():
    # list of stocks to track
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA", "AMD", "MU"]
    stocks = []

    for symbol in symbols:
        data = get_stock_data(symbol)
        stocks.append(data)
        print(f"Fetched {symbol}: ${data['price']}")

    # save html to docs folder for github pages
    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w") as f:
        f.write(generate_html(stocks))

    print("Generated docs/index.html")


if __name__ == "__main__":
    main()
