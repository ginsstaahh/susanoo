from datetime import datetime
from helpers.session import session
from helpers.tables import Weather, Pollution, City

def kelvin_to_celsius(kelvin):
    celsius = round(kelvin - 273.15, 2)
    return celsius

def transform_weather_data(task_instance):
    """refines weather data to an SQL format and saves to database
    Args:
        task_instance - The task instance from Airflow to pull XCom data
    """
    weather_data = task_instance.xcom_pull(task_ids='get_weather_data')
    weather = Weather(
        city = weather_data['name'],
        country = weather_data['sys']['country'], 
        base = weather_data['base'],
        temperature = kelvin_to_celsius(weather_data['main']['temp']),
        description = weather_data['weather'][0]['description'],
        time = weather_data['dt'],
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
    """refines pollution data to an SQL format and saves to database
    Args:
        task_instance - The task instance from Airflow to pull XCom data
        city - The city for which the pollution data was fetched
        country - The country of the city
    """
    pollution_data = task_instance.xcom_pull(task_ids='get_pollution_data')
    pollution = Pollution(
        city = city,
        country = country,
        time = pollution_data['list'][0]['dt'],
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
    """refines city data to an SQL format and saves to database
    args:
        task_instance - The task instance from Airflow to pull XCom data
    """
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