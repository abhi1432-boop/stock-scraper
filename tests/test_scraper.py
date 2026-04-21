import pytest
from scraper import get_stock_data, generate_html

MINIMAL_STOCK = {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "price": 189.50,
    "change": 1.50,
    "change_percent": 0.84,
    "open": 188.0,
    "high": 190.0,
    "low": 187.0,
    "timestamp": "2024-01-01 12:00:00",
}

FULL_STOCK = {
    **MINIMAL_STOCK,
    "prev_close": 188.0,
    "week_52_high": 220.0,
    "week_52_low": 150.0,
    "avg_volume": 50000000,
    "shares_outstanding": 15000000000,
    "market_cap": 2900000000000,
    "beta": 1.25,
    "eps_ttm": 6.43,
    "pe_ttm": 29.5,
    "forward_pe": 26.0,
    "price_to_sales": 7.8,
    "ev_ebitda": 22.0,
    "revenue_ttm": 390000000000,
    "ebitda": 130000000000,
    "gross_margin": 0.44,
    "net_margin": 0.26,
    "roe": 1.60,
    "roic": 0.30,
    "debt_to_equity": 150.0,
    "cash": 65000000000,
    "free_cash_flow": 100000000000,
    "earnings_date": "2025-07-31",
    "dividend_date": None,
    "last_split": None,
    "return_5d": 1.2,
    "return_1m": -2.5,
    "return_3m": 5.0,
    "return_ytd": -8.1,
    "return_1y": 12.3,
    "return_5y": 210.0,
}


# ── Live API tests (integration) ──────────────────────────────────────────────

def test_get_stock_data_returns_dict():
    result = get_stock_data("AAPL")
    assert isinstance(result, dict)


def test_get_stock_data_has_base_keys():
    result = get_stock_data("AAPL")
    base_keys = ["symbol", "name", "price", "change", "change_percent", "open", "high", "low", "timestamp"]
    for key in base_keys:
        assert key in result, f"Missing key: {key}"


def test_get_stock_data_has_extended_keys():
    result = get_stock_data("AAPL")
    extended_keys = [
        "prev_close", "week_52_high", "week_52_low", "market_cap", "beta",
        "eps_ttm", "pe_ttm", "forward_pe", "revenue_ttm", "gross_margin",
        "net_margin", "roe", "debt_to_equity", "cash", "free_cash_flow",
        "return_5d", "return_1m", "return_3m", "return_ytd", "return_1y", "return_5y",
    ]
    for key in extended_keys:
        assert key in result, f"Missing key: {key}"


def test_price_is_a_number():
    result = get_stock_data("AAPL")
    assert isinstance(result["price"], (int, float))


def test_symbol_matches():
    result = get_stock_data("GOOGL")
    assert result["symbol"] == "GOOGL"


# ── generate_html unit tests (no network) ────────────────────────────────────

def test_generate_html_returns_string():
    result = generate_html([MINIMAL_STOCK])
    assert isinstance(result, str)


def test_generate_html_contains_stock_details():
    result = generate_html([MINIMAL_STOCK])
    assert "AAPL" in result
    assert "Apple Inc." in result
    assert "Open" in result
    assert "High" in result
    assert "Low" in result
    assert "Investment Agent" in result
    assert "Ask me what to invest in" in result


def test_generate_html_handles_missing_optional_fields():
    result = generate_html([MINIMAL_STOCK])
    assert isinstance(result, str)
    assert "AAPL" in result


def test_generate_html_with_full_stock_data():
    result = generate_html([FULL_STOCK])
    assert "AAPL" in result
    assert "Apple Inc." in result
    assert "Mkt Cap" in result
    assert "P/E" in result
    assert "Beta" in result


def test_generate_html_return_colors():
    pos = {**MINIMAL_STOCK, "return_5d": 2.5}
    neg = {**MINIMAL_STOCK, "return_5d": -1.3}
    html_pos = generate_html([pos])
    html_neg = generate_html([neg])
    assert "positive" in html_pos
    assert "negative" in html_neg
