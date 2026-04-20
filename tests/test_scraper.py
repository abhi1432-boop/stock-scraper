import pytest
from scraper import get_stock_data, generate_html


def test_get_stock_data_returns_dict():
    result = get_stock_data("AAPL")
    assert isinstance(result, dict)


def test_get_stock_data_has_correct_keys():
    result = get_stock_data("AAPL")
    assert "symbol" in result
    assert "price" in result
    assert "previous_close" in result
    assert "change" in result
    assert "timestamp" in result


def test_price_is_a_number():
    result = get_stock_data("AAPL")
    assert isinstance(result["price"], (int, float))


def test_symbol_matches():
    result = get_stock_data("GOOGL")
    assert result["symbol"] == "GOOGL"


def test_generate_html_returns_string():
    fake_stocks = [{"symbol": "AAPL", "price": 189.50, "change": 1.50, "timestamp": "2024-01-01"}]
    result = generate_html(fake_stocks)
    assert isinstance(result, str)


def test_generate_html_contains_symbol():
    fake_stocks = [{"symbol": "AAPL", "price": 189.50, "change": 1.50, "timestamp": "2024-01-01"}]
    result = generate_html(fake_stocks)
    assert "AAPL" in result
