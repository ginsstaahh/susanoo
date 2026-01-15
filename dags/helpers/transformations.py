from datetime import datetime
import json

def kelvin_to_celsius(kelvin):
    celsius = round(kelvin - 273.15, 2)
    return celsius

def transform_weather_data(task_instance):
    """processes raw JSON weather data to a refined format
    Args:
        task_instance - The task instance from Airflow to pull XCom data
    """
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

    # Save transformed data to a local JSON file with the current date
    dt_string = datetime.fromtimestamp(weather_data['dt']).strftime("%Y-%m-%d")
    with open(f'weather/weather-{dt_string}.json', 'a') as file:
        json.dump(transformed_data, file)
        file.write('\n')

def transform_pollution_data(task_instance, city, country):    
    """processes raw JSON pollution data to a refined format
    Args:
        task_instance - The task instance from Airflow to pull XCom data
        city - The city for which the pollution data is being processed
        country - The country of the city
    """
    pollution_data = task_instance.xcom_pull(task_ids='get_pollution_data')
    city = city
    country = country

    transformed_data = {
        'city': city,
        'country': country,
        'time': datetime.fromtimestamp(pollution_data['list'][0]['dt']).strftime("%Y-%m-%d %H:%M:%S"),
        'AQI': pollution_data['list'][0]['main']['aqi'],
        'CO': pollution_data['list'][0]['components']['co'],
        'NO': pollution_data['list'][0]['components']['no'],
        'NO2': pollution_data['list'][0]['components']['no2'],
        'O3': pollution_data['list'][0]['components']['o3'],
        'SO2': pollution_data['list'][0]['components']['so2'],
        'PM2_5': pollution_data['list'][0]['components']['pm2_5'],
        'PM10': pollution_data['list'][0]['components']['pm10'],
        'NH3': pollution_data['list'][0]['components']['nh3'],
    }

    # Save transformed data to a local JSON file with the current date
    dt_string = datetime.fromtimestamp(pollution_data['list'][0]['dt']).strftime("%Y-%m-%d")
    with open(f'pollution/pollution-{dt_string}.json', 'a') as file:
        json.dump(transformed_data, file)
        file.write('\n')

    
    def transform_city_data(task_instance):
        """Processes raw JSON data to extract contextual data of the city
        Args:
            task_instance - The task instance from Airflow to pull XCom data
        """
        weather_data = task_instance.xcom_pull(task_ids='get_city_data')
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