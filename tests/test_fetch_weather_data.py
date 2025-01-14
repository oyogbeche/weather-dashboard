import pytest
import requests
import logging
from unittest.mock import patch, MagicMock
from src.weather_dashboard import WeatherDashboard 

# Mock API key for testing
MOCK_API_KEY = "mock_api_key"

@pytest.fixture
def weather_dashboard():
    """Fixture to create a WeatherDashboard instance with a mock API key."""
    dashboard = WeatherDashboard()
    dashboard.api_key = MOCK_API_KEY
    return dashboard

@patch("requests.get")
def test_fetch_weather_current(mock_get, weather_dashboard):
    """Test fetching current weather data."""
    # Arrange
    city = "Lagos"
    data_type = "current"
    mock_response_data = {"weather": [{"description": "clear sky"}], "main": {"temp": 30}}
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Act
    result = weather_dashboard.fetch_weather(city, data_type)

    # Assert
    assert result == mock_response_data
    mock_get.assert_called_once_with(
        "http://api.openweathermap.org/data/2.5/weather",
        params={"q": city, "appid": MOCK_API_KEY, "units": "metric"}
    )

@patch("requests.get")
def test_fetch_weather_forecast(mock_get, weather_dashboard):
    """Test fetching weather forecast data."""
    # Arrange
    city = "Lagos"
    data_type = "forecast"
    mock_response_data = {"list": [{"main": {"temp": 29}}, {"main": {"temp": 28}}]}
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Act
    result = weather_dashboard.fetch_weather(city, data_type)

    # Assert
    assert result == mock_response_data
    mock_get.assert_called_once_with(
        "http://api.openweathermap.org/data/2.5/forecast",
        params={"q": city, "appid": MOCK_API_KEY, "units": "metric"}
    )

@patch("requests.get")
def test_fetch_weather_invalid_data_type(mock_get, weather_dashboard, caplog):
    """Test fetching weather with an invalid data type."""
    # Arrange
    city = "Lagos"
    data_type = "invalid"

    # Act
    with caplog.at_level(logging.INFO):
        result = weather_dashboard.fetch_weather(city, data_type)

    # Assert
    assert result is None
    mock_get.assert_not_called()
    assert "Invalid data type 'invalid', must be 'current' or 'forecast'" in caplog.text


@patch("requests.get")
def test_fetch_weather_request_exception(mock_get, weather_dashboard, caplog):
    """Test handling a requests exception."""
    # Arrange
    city = "Lagos"
    data_type = "current"
    mock_get.side_effect = requests.exceptions.RequestException("API error")

    # Act
    result = weather_dashboard.fetch_weather(city, data_type)

    # Assert
    assert result is None
    mock_get.assert_called_once_with(
        "http://api.openweathermap.org/data/2.5/weather",
        params={"q": city, "appid": MOCK_API_KEY, "units": "metric"}
    )
    assert f"Error fetching weather data for '{city}': API error" in caplog.text
