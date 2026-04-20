import requests
import json
import os
from datetime import datetime


def get_stock_data(symbol):
    # fetch stock data from yahoo finance for a given stock symbol
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    data = response.json()

    # pull out the price info from the response
    price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
    previous_close = data["chart"]["result"][0]["meta"]["chartPreviousClose"]
    change = round(price - previous_close, 2)

    return {
        "symbol": symbol,
        "price": price,
        "previous_close": previous_close,
        "change": change,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def generate_html(stocks):
    # build the html page that will be displayed on github pages
    rows = ""
    for stock in stocks:
        color = "green" if stock["change"] >= 0 else "red"
        rows += f"""
        <tr>
            <td>{stock["symbol"]}</td>
            <td>${stock["price"]}</td>
            <td style="color:{color}">{stock["change"]}</td>
            <td>{stock["timestamp"]}</td>
        </tr>
        """

    return f"""
    <html>
    <head><title>Stock Tracker</title></head>
    <body>
        <h1>Stock Tracker</h1>
        <table border="1">
            <tr>
                <th>Symbol</th>
                <th>Price</th>
                <th>Change</th>
                <th>Last Updated</th>
            </tr>
            {rows}
        </table>
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
