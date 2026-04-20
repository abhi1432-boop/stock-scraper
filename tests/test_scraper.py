import pytest
from scraper import get_stock_data, generate_html


def test_get_stock_data_returns_dict():
    result = get_stock_data("AAPL")
    assert isinstance(result, dict)


def test_get_stock_data_has_correct_keys():
    result = get_stock_data("AAPL")
    assert "symbol" in result
    assert "name" in result
    assert "price" in result
    assert "change" in result
    assert "change_percent" in result
    assert "open" in result
    assert "high" in result
    assert "low" in result
    assert "timestamp" in result


def test_price_is_a_number():
    result = get_stock_data("AAPL")
    assert isinstance(result["price"], (int, float))


def test_symbol_matches():
    result = get_stock_data("GOOGL")
    assert result["symbol"] == "GOOGL"


def test_generate_html_returns_string():
    fake_stocks = [{
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "price": 189.50,
        "change": 1.50,
        "change_percent": 0.84,
        "open": 188.0,
        "high": 190.0,
        "low": 187.0,
        "timestamp": "2024-01-01 12:00:00"
    }]
    result = generate_html(fake_stocks)
    assert isinstance(result, str)


def test_generate_html_contains_stock_details():
    fake_stocks = [{
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "price": 189.50,
        "change": 1.50,
        "change_percent": 0.84,
        "open": 188.0,
        "high": 190.0,
        "low": 187.0,
        "timestamp": "2024-01-01 12:00:00"
    }]
    result = generate_html(fake_stocks)
    assert "AAPL" in result
    assert "Apple Inc." in result
    assert "Open" in result
    assert "High" in result
    assert "Low" in result
