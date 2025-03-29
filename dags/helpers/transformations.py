from datetime import datetime
from helpers.session import session
from helpers.tables import Weather, Pollution, City

def kelvin_to_celsius(kelvin):
    celsius = round(kelvin - 273.15, 2)
    return celsius

def transform_weather_data(task_instance):
    weather_data = task_instance.xcom_pull(task_ids='get_weather_data')
    weather = Weather(
        city = weather_data['name'],
        country = weather_data['sys']['country'], 
        base = weather_data['base'],
        temperature = kelvin_to_celsius(weather_data['main']['temp']),
        description = weather_data['weather'][0]['description'],
        time = datetime.fromtimestamp(weather_data['dt']).strftime("%Y-%m-%d %H:%M:%S"),
        min_temp = kelvin_to_celsius(weather_data['main']['temp_min']),
        max_temp = kelvin_to_celsius(weather_data['main']['temp_max']),
        pressure = weather_data['main']['pressure'],
        humidity = weather_data['main']['humidity'],
        visibility = weather_data['visibility'],
        wind_speed = weather_data['wind']['speed'],
        wind_deg = weather_data['wind']['deg']
    )
    session.add(weather)
    session.commit()

def transform_pollution_data(task_instance, city, country):
    pollution_data = task_instance.xcom_pull(task_ids='get_pollution_data')
    pollution = Pollution(
        city = city,
        country = country,
        time = datetime.fromtimestamp(pollution_data['list'][0]['dt']).strftime("%Y-%m-%d %H:%M:%S"),
        aqi = pollution_data['list'][0]['main']['aqi'],
        co = pollution_data['list'][0]['components']['co'],
        no = pollution_data['list'][0]['components']['no'],
        no2 = pollution_data['list'][0]['components']['no2'],
        o3 = pollution_data['list'][0]['components']['o3'],
        so2 = pollution_data['list'][0]['components']['so2'],
        pm2_5 = pollution_data['list'][0]['components']['pm2_5'],
        pm10 = pollution_data['list'][0]['components']['pm10'],
        nh3 = pollution_data['list'][0]['components']['nh3']
    )
    session.add(pollution)
    session.commit()

def transform_city_data(task_instance):
    """uses the HTTP response from Openweather to store
    dimension data of the city being queried in cities SQL table"""
    weather_data = task_instance.xcom_pull(task_ids='get_city_data')
    city = City(
        city = weather_data['name'],
        country = weather_data['sys']['country'],
        longitude = weather_data['coord']['lon'],
        latitude = weather_data['coord']['lat'],
        timezone = weather_data['timezone']
    )
    session.add(city)
    session.commit()