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

    def fetch_weather(self, city, data_type):
        """Fetch weather data from openweather API"""
        base_url= {
            "current": "http://api.openweathermap.org/data/2.5/weather",
            "forecast": "http://api.openweathermap.org/data/2.5/forecast"
        }.get(data_type)

        if not base_url:
            logging.info(f"Invalid data type '{data_type}', must be 'current' or 'forecast'")
            return None
        
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
            return None

    def save_to_s3(self, data, city, data_type):
        """save weather data to s3 bucket"""
        if not data:
            logging.error(f"No data provided for '{data_type}' weather")
            return False
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f"weather-data/{data_type}/{city}-{timestamp}.json"

        # Add a timestamp to the data 
        data['timestamp'] = timestamp

        serialized_data = json.dumps(data)

        logging.info (f"Saving {data_type} data for {city} to S3")

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=serialized_data,
                ContentType='application/json'
            )
            logging.info(f"Saved '{data_type}' data for '{city}' to S3 as '{filename}' successfully ")
            return True
        except Exception as e:
            logging.error(f"Failed to save '{data_type}' data for '{city}' to S3: {e}")
            return False

def main():
    try:
        dashboard = WeatherDashboard()
        dashboard.create_bucket_if_not_exists()

        # cities to fetch weather data for
        cities = ["Lagos", "Abuja", "Ohio", "Georgia", "Houston"]

        for city in cities:
            logging.info(f"\nFetching current weather for {city}...")
            weather_data = dashboard.fetch_weather(city, data_type="current")

            if weather_data:
                temp = weather_data['main']['temp']
                feels_like = weather_data['main']['feels_like']
                humidity = weather_data['main']['humidity']
                description = weather_data['weather'][0]['description']

                logging.info(
                    f"Temperature: {temp}°C\n"
                    f"Feels like: {feels_like}°C\n"
                    f"Humidity: {humidity}%\n"
                    f"Conditions: {description}\n"
                )

                # save to s3
                dashboard.save_to_s3(weather_data, city, data_type="current")
            
            logging.info(f"\nWeather forecast for {city}:")
            forecast_weather = dashboard.fetch_weather(city, data_type="forecast")
            
            if forecast_weather:
                for forecast in forecast_weather['list'][:3]:  # Display first 3 forecast entries
                    forecast_time = forecast['dt_txt']
                    forecast_temp = forecast['main']['temp']
                    forecast_desc = forecast['weather'][0]['description']
                    logging.info(
                        f"Forecast time: {forecast_time}\n"
                        f"Forecast Temperature: {forecast_temp}°C\n"
                        f"Forcast Conditions: {forecast_desc}\n"
                    )
                    # save to s3
                    dashboard.save_to_s3(weather_data, city, data_type="forecast")
            else:
                logging.warning(f"Weather data for '{city}' could not be fetched")
    except Exception as e:
        logging.critical(f"An error occured: {e}")

if __name__ == "__main__":
    main()

