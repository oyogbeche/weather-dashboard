# 30 Days DevOps Challenge - Weather Dashboard

Building a weather data collection system using AWS S3 and OpenWeather API

## Project Overview
This project is a Weather Data Collection System that demonstrates core DevOps principles by combining:
- External API Integration (OpenWeather API)
- Cloud Storage (AWS S3)
- Infrastructure as Code
- Version Control (Git)
- Python Development
- Error Handling
- Environment Management

## Features
- Fetches real-time weather data for multiple cities
- Displays temperature (°C), humidity, and weather conditions
- Automatically stores weather data in AWS S3
- Supports multiple cities tracking
- Timestamps all data for historical tracking

## Technical Architecture
- **Language:** Python 3.9
- **Cloud Provider:** AWS (S3)
- **External API:** OpenWeather API
- **Dependencies:** 
  - boto3 (AWS SDK)
  - python-dotenv
  - requests
  - pytest

## Project Structure
```markdown
weather-dashboard/
├──.github/workflows          # CI for automated testing
├── src/                      # Source code for the weather dashboard
│   ├── __init__.py           # Initialization file for the package
│   └── weather_dashboard.py  # Main weather dashboard application logic
├── tests/                    # Unit and integration tests
├── .env.example              # Example for configurable Env variables
├── .gitignore                # ignored files
├── README.md                 # Project documentation
└── requirements.txt          # Python dependencies
```

## Setup Instructions
1. Clone the repository:
```bash
    git clone https://github.com/oyogbeche/weather-dashboard.git
    cd weather-dashboard
```

2. Create and Activate venv:
```bash
    python -m venv myenv
    myenv\Scripts\Activate.ps1
```


3. Install dependencies:
```bash
    pip install -r requirements.txt
```

4. Configure environment variables (.env):

    See the `.env.example` for a list of configurable environment variables

5. Configure AWS credentials:
```bash
    aws configure
```
6. Run the application:
```bash
    python src/weather_dashboard.py
```
### What I Learned
- Python best practices for API integration
- Error handling in distributed systems
- Python tests for code quality
- CI/CD for automated testing


### Future Enhancements
- Implement data visualization