from datetime import datetime
import json

def kelvin_to_celsius(kelvin):
    celsius = round(kelvin - 273.15, 2)
    return celsius

def transform_data(task_instance):
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

    # Save transformed data to a local json file using the current time as a schema
    now = datetime.now()
    dt_string = now.strftime("%Y_%m_%d-%H_%M_%S")
    filename = f'van_weather-{dt_string}.json'

    with open(filename, 'w') as f:
        json.dump(transformed_data, f)
    return filename

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

    with open('city_dimensions.json', 'w') as f:
        json.dump(transformed_data, f)