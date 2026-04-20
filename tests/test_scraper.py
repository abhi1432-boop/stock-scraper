import pytest
from scraper import get_stock_data, generate_html


def test_get_stock_data_returns_dict():
    # make sure the function returns a dictionary
    result = get_stock_data("AAPL")
    assert type(result) == dict


def test_get_stock_data_has_correct_keys():
    # make sure all expected keys are present in the response
    result = get_stock_data("AAPL")
    assert "symbol" in result
    assert "price" in result
    assert "previous_close" in result
    assert "change" in result
    assert "timestamp" in result


def test_price_is_a_number():
    # make sure price comes back as a number and not a string
    result = get_stock_data("AAPL")
    assert type(result["price"]) == float or type(result["price"]) == int


def test_symbol_matches():
    # make sure the symbol returned matches what we requested
    result = get_stock_data("GOOGL")
    assert result["symbol"] == "GOOGL"


def test_generate_html_returns_string():
    # make sure generate_html returns a string
    fake_stocks = [{"symbol": "AAPL", "price": 189.50, "change": 1.50,
                    "change_pct": 0.84, "name": "Apple Inc.",
                    "open": 188.0, "high": 190.0, "low": 187.0,
                    "timestamp": "2024-01-01"}]
    result = generate_html(fake_stocks)
    assert type(result) == str


def test_generate_html_contains_symbol():
    # make sure the stock symbol appears in the generated html
    fake_stocks = [{"symbol": "AAPL", "price": 189.50, "change": 1.50,
                    "change_pct": 0.84, "name": "Apple Inc.",
                    "open": 188.0, "high": 190.0, "low": 187.0,
                    "timestamp": "2024-01-01"}]
    result = generate_html(fake_stocks)
    assert "AAPL" in result