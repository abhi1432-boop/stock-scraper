import os
import time
from flask import Flask, request, jsonify, send_from_directory
from scraper import get_stock_data, STOCKS
from chatbot import StockChatbot

# Serve the React build when available, fall back to the scraper-generated static site
_DIST = "frontend/dist"
_STATIC = "docs"
_static_folder = _DIST if os.path.isdir(_DIST) else _STATIC

app = Flask(__name__, static_folder=_static_folder, static_url_path="")

_chatbot: StockChatbot | None = None

def _get_chatbot() -> StockChatbot:
    global _chatbot
    if _chatbot is None:
        _chatbot = StockChatbot()
    return _chatbot


_stock_cache: dict = {}
STOCK_TTL = 300  # 5 minutes


def _cached_stock(symbol: str) -> dict:
    now = time.time()
    if symbol in _stock_cache:
        cached_at, data = _stock_cache[symbol]
        if now - cached_at < STOCK_TTL:
            return data
    data = get_stock_data(symbol)
    _stock_cache[symbol] = (now, data)
    return data


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/stocks")
def all_stocks():
    result = {symbol: _cached_stock(symbol) for symbol in STOCKS}
    return jsonify(result)


@app.route("/api/stocks/<ticker>")
def single_stock(ticker: str):
    ticker = ticker.upper()
    if ticker not in STOCKS:
        return jsonify({"error": f"Unknown ticker: {ticker}"}), 404
    return jsonify(_cached_stock(ticker))


@app.route("/api/chat", methods=["POST"])
def chat():
    body = request.get_json(silent=True) or {}
    question = (body.get("question") or "").strip()
    tickers = body.get("tickers") or list(STOCKS.keys())

    if not question:
        return jsonify({"error": "question is required"}), 400

    tickers = [t.upper() for t in tickers if t.upper() in STOCKS] or list(STOCKS.keys())
    stock_data = {t: _cached_stock(t) for t in tickers}

    try:
        bot = _get_chatbot()
        answer = bot.answer(question, stock_data)
        return jsonify({"answer": answer})
    except ValueError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
