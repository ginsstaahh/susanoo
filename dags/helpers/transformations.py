from datetime import datetime

def kelvin_to_celsius(kelvin):
    celsius = round(kelvin - 273.15, 2)
    return celsius

def transform_weather_data(task_instance):
    weather_data = task_instance.xcom_pull(task_ids='get_weather_data')
    transformed_data =  [[
            weather_data['name'],
            weather_data['sys']['country'],
            weather_data['base'],
            weather_data['weather'][0]['description'],
            datetime.fromtimestamp(weather_data['dt']).strftime("%Y-%m-%d %H:%M:%S"),
            kelvin_to_celsius(weather_data['main']['temp']),
            kelvin_to_celsius(weather_data['main']['temp_min']),
            kelvin_to_celsius(weather_data['main']['temp_max']),
            weather_data['main']['pressure'],
            weather_data['main']['humidity'],
            weather_data['visibility'],
            weather_data['wind']['speed'],
            weather_data['wind']['deg']
        ]]

    return transformed_data


def transform_pollution_data(task_instance, city, country):
    pollution_data = task_instance.xcom_pull(task_ids='get_pollution_data')
    transformed_data = [[
            city,
            country,
            datetime.fromtimestamp(pollution_data['list'][0]['dt']).strftime("%Y-%m-%d %H:%M:%S"),
            pollution_data['list'][0]['main']['aqi'],
            pollution_data['list'][0]['components']['co'],
            pollution_data['list'][0]['components']['no'],
            pollution_data['list'][0]['components']['no2'],
            pollution_data['list'][0]['components']['o3'],
            pollution_data['list'][0]['components']['so2'],
            pollution_data['list'][0]['components']['pm2_5'],
            pollution_data['list'][0]['components']['pm10'],
            pollution_data['list'][0]['components']['nh3'],
    ]]

    return transformed_data


def transform_city_data(task_instance):
    """process raw JSON data to dimension data of the city"""
    weather_data = task_instance.xcom_pull(task_ids='get_city_data')
    transformed_data = [[
        weather_data['name'],
        weather_data['sys']['country'],
        weather_data['coord']['lon'],
        weather_data['coord']['lat'],
        weather_data['timezone'],
    ]]

    return transformed_data