from datetime import datetime
import json
import pandas as pd

def kelvin_to_celsius(kelvin):
    celsius = round(kelvin - 273.15, 2)
    return celsius

def transform_weather_data(task_instance):
    weather_data = task_instance.xcom_pull(task_ids='get_weather_data')
    transformed_data = {
        'city': weather_data['name'],
        'country': weather_data['sys']['country'],
        'base': weather_data['base'],
        'description': weather_data['weather'][0]['description'],
        'time' : datetime.fromtimestamp(weather_data['dt']).strftime("%Y-%m-%d %H:%M:%S"),
        'temperature': kelvin_to_celsius(weather_data['main']['temp']),
        'min_temp': kelvin_to_celsius(weather_data['main']['temp_min']),
        'max_temp': kelvin_to_celsius(weather_data['main']['temp_max']),
        'pressure': weather_data['main']['pressure'],
        'humidity': weather_data['main']['humidity'],
        'visibility': weather_data['visibility'],
        'wind_speed': weather_data['wind']['speed'],
        'wind_deg': weather_data['wind']['deg']
    }

    # Save transformed data to a local json file with the current date
    dt_string = datetime.now().strftime("%Y-%m-%d")
    with open(f'vancouver-weather-{dt_string}.json', 'a') as file:
        json.dump(transformed_data, file)
        file.write('\n')

cities = {
    'Vancouver': {
        "country": "CA",
        "longitude": -123.1193,
        "latitude": 49.2497,
        "timezone": -28800
    },
    'Los Angeles': {
        "country": "US",
        "longitude": -118.2437,
        "latitude": 34.0522,
        "timezone": -28800
    },
    'San Francisco': {
        "country": "US",
        "longitude": -122.4194,
        "latitude": 37.7749,
        "timezone": -28800
    },
    'Tokyo': {
        "country": "JP",
        "longitude": 139.6917,
        "latitude": 35.6895,
        "timezone": 32400
    },
    'Beijing': {
        "country": "CN",
        "longitude": 116.3972,
        "latitude": 39.9075,
        "timezone": 28800
    },
    'Hong Kong': {
        "country": "HK",
        "longitude": 114.1577,
        "latitude": 22.2855,
        "timezone": 28800
    },
    'Manila': {
        "country": "PH",
        "longitude": 120.9822,
        "latitude": 14.6042,
        "timezone": 28800
    },
    'Sydney': {
        "country": "AU",
        "longitude": 151.2073,
        "latitude": -33.8679,
        "timezone": 39600
    }
}

def transform_pollution_data(task_instance):
    pollution_data = task_instance.xcom_pull(task_ids='get_pollution_data')
    longitude = pollution_data['coord']['lon']
    latitude = pollution_data['coord']['lat']

    data = []
    with open('/home/ginsstaahh/Documents/susanoo/city_dimensions.json', 'r') as file:
        for line in file:
            data.append(json.loads(line))

    df = pd.DataFrame(data)
    df = df.where(df['longitude'] == longitude).where(df['latitude'] == latitude)
    print(df['city'])
    print(df['country'])

    transformed_data = {
        'city': df['city'].values[0],
        'country': df['country'].values[0],
        'time': datetime.fromtimestamp(pollution_data['list'][0]['dt']).strftime("%Y-%m-%d %H:%M:%S"),
        'air_quality_index': pollution_data['list'][0]['main']['aqi'],
        'CO': pollution_data['list'][0]['components']['co'],
        'NO': pollution_data['list'][0]['components']['no'],
        'NO2': pollution_data['list'][0]['components']['no2'],
        'O3': pollution_data['list'][0]['components']['o3'],
        'SO2': pollution_data['list'][0]['components']['so2'],
        'PM2_5': pollution_data['list'][0]['components']['pm2_5'],
        'PM10': pollution_data['list'][0]['components']['pm10'],
        'NH3': pollution_data['list'][0]['components']['nh3'],
    }
    
    # Save transformed data to a local json file with the current date
    dt_string = datetime.now().strftime("%Y-%m-%d")
    with open(f'vancouver-pollution-{dt_string}.json', 'a') as file:
        json.dump(transformed_data, file)
        file.write('\n')

def save_city_dimensions(task_instance):
    """save_city_dimensions uses the HTTP response from Openweather to store
    dimension data of the city being queried in a json file"""
    weather_data = task_instance.xcom_pull(task_ids='get_weather_data')
    transformed_data = {
        'city': weather_data['name'],
        'country': weather_data['sys']['country'],
        'longitude': weather_data['coord']['lon'],
        'latitude': weather_data['coord']['lat'],
        'timezone': weather_data['timezone'],
    }

    with open('city_dimensions.json', 'a') as file:
        json.dump(transformed_data, file)
        file.write('\n')