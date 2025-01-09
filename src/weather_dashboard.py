import os
import boto3
import requests
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# load environment variables

load_dotenv()

# configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class WeatherDashboard:
    def __init__(self):
        """Initialize the WeatherDashboard with API keys and S3 client"""
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')
        self.region = os.getenv('AWS_REGION')
        if not self.api_key or not self.bucket_name:
            raise ValueError("Missing required env variables: OPENWEATHER_API_KEY OR AWS_BUCKET_NAME")
        self.s3_client = boto3.client('s3')

    
    def create_bucket_if_not_exists(self):
        """Create s3 bucket if it does not exist"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logging.info(f"s3 Bucket '{self.bucket_name}' already exists")
        except:
            logging.info(f"Creating bucket '{self.bucket_name}'")
        try:
            self.s3_client.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': self.region
                }
            )
            logging.info(f"'{self.bucket_name}' created successfully in '{self.region}'")
        except Exception as e:
            logging.error(f"failed to create bucket: {e}")

    def fetch_weather(self, city,):
        """Fetch weather data from openweather API"""
        base_url= "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        try: 
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            logging.info(f"weather data for '{city}' fetched successfully")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching weather data for '{city}': {e}")
            return none

    def save_to_s3(self, weather_data, city):
        """save weather data to s3 bucket"""
        if not weather_data:
            logging.error(f"No weather data for '{city}'")
            return false
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f"weather-data/{city}-{timestamp}.json"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=json.dumps(weather_data),
                ContentType='application/json'
            )
            logging.info(f"Weather data for '{city}' saved to S3 as '{filename}'")
            return True
        except Exception as e:
            logging.error(f"Failed to save weather data for '{city}' to S3: {e}")
            return False

def main():
    try:
        dashboard = WeatherDashboard()
        dashboard.create_bucket_if_not_exists()

        # cities to fetch weather data for
        cities = ["Lagos", "Abuja", "Ohio", "Georgia", "Houston"]

        for city in cities:
            logging.info(f"fetching weather data for '{city}'")
            weather_data = dashboard.fetch_weather(city)

            if weather_data:
                temp = weather_data['main']['temp']
                feels_like = weather_data['main']['feels_like']
                humidity = weather_data['main']['humidity']
                description = weather_data['weather'][0]['description']

                logging.info(
                    f"Temperature: {temp}°F\n"
                    f"Feels like: {feels_like}°F\n"
                    f"Humidity: {humidity}%\n"
                    f"Conditions: {description}\n"
                )

                # save to s3
                dashboard.save_to_s3(weather_data, city)
            else:
                logging.warning(f"Weather data for '{city}' could not be fetched")
    except Exception as e:
        logging.critical(f"An error occured: {e}")

if __name__ == "__main__":
    main()

