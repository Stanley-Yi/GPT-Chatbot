from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def call_google(query, location=None):
    base_url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "hl": "en",
        "gl": "us",
        "google_domain": "google.com",
        "api_key": os.getenv('SERPAPI_KEY')
    }

    if location is not None:
        params['location'] = location

    response = requests.get(base_url, params=params)

    return response.text  


def get_current_weather(location, unit):
    base_url = "http://api.weatherapi.com/v1/current.json"
    query_params = {
        'key': os.getenv('WEATHER_API'),
        'q': location,
        'aqi': 'no'
    }
    response = requests.get(base_url, params=query_params)

    if unit == 'fahrenheit':
        return response.json()['current']['temp_f']
    else:
        return response.json()['current']['temp_c']
    
    
    
def get_past_n_day_weather(location, unit, days):
    if not days >= 0:
        return 'Please give a positive day number'
    
    base_url = "http://api.weatherapi.com/v1/history.json"
    
    result = ''
    
    for i in range(1, days + 1):
        past_day = datetime.now() - timedelta(i)
        past_day = past_day.strftime('%Y-%m-%d')
        
        query_params = {
            'key': os.getenv('WEATHER_API'),
            'q': location,
            'dt': past_day
        }
        
        response = requests.get(base_url, params=query_params)
        
        if unit == 'fahrenheit':
            result += f' === Past {str(i)} day: ' + str(response.json()['forecast']['forecastday'][0]['hour'][0]['temp_f']) + f' {unit} === '
        else:
            result += f' === Past {str(i)} day: ' + str(response.json()['forecast']['forecastday'][0]['hour'][0]['temp_c']) + f' {unit} === '
        
    return result