import requests
import os
from datetime import datetime

COMPANY_NAMES = {
    "AAPL": "Apple Inc.",
    "GOOGL": "Alphabet Inc.",
    "MSFT": "Microsoft Corp.",
    "AMZN": "Amazon.com, Inc."
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
            <p class=\"updated\">Last updated: {page_timestamp}</p>
        </div>
    </body>
    </html>
    """


def main():
    # list of stocks to track
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN"]
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
