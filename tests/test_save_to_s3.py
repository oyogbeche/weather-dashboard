import pytest
from unittest.mock import patch, MagicMock
from src.weather_dashboard import WeatherDashboard

@patch("boto3.client")
def test_save_to_s3_success(mock_boto_client):
    # Mock S3 client
    mock_s3 = mock_boto_client.return_value
    mock_s3.put_object.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

    dashboard = WeatherDashboard()
    weather_data = {"main": {"temp": 85.0}, "weather": [{"description": "clear sky"}]}
    success = dashboard.save_to_s3(weather_data, "Lagos", "current")

    assert success is True
    mock_s3.put_object.assert_called_once()


@patch("boto3.client")
def test_save_to_s3_failure(mock_boto_client):
    # Mock S3 client to raise an error
    mock_s3 = mock_boto_client.return_value
    mock_s3.put_object.side_effect = Exception("S3 error")

    dashboard = WeatherDashboard()
    weather_data = {"main": {"temp": 85.0}, "weather": [{"description": "clear sky"}]}
    success = dashboard.save_to_s3(weather_data, "Lagos", "current")

    assert success is False
    mock_s3.put_object.assert_called_once()