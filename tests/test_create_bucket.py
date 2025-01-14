import pytest
from unittest.mock import patch, Mock
from botocore.exceptions import ClientError
from src.weather_dashboard import WeatherDashboard

@pytest.mark.parametrize(
    "head_bucket_side_effect, expected_create_bucket_called",
    [
        (None, False),  # Bucket exists
        (ClientError({"Error": {"Code": "404", "Message": "Not Found"}}, "HeadBucket"), True),  # Bucket does not exist
    ],
)
@patch("boto3.client")
def test_create_bucket_if_not_exists(mock_boto_client, head_bucket_side_effect, expected_create_bucket_called):
    """Test create_bucket_if_not_exists for both existing and non-existing buckets."""
    # Arrange
    mock_s3_client = Mock()
    mock_boto_client.return_value = mock_s3_client
    mock_s3_client.head_bucket.side_effect = head_bucket_side_effect
    weather_dashboard = WeatherDashboard()

    # Act
    weather_dashboard.create_bucket_if_not_exists()

    # Assert
    if expected_create_bucket_called:
        mock_s3_client.create_bucket.assert_called_once_with(
            Bucket=weather_dashboard.bucket_name,
            CreateBucketConfiguration={"LocationConstraint": weather_dashboard.region},
        )
    else:
        mock_s3_client.create_bucket.assert_not_called()
    mock_s3_client.head_bucket.assert_called_once_with(Bucket=weather_dashboard.bucket_name)
