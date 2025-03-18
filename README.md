# Introduction
This Airflow project logs weather data for Vancouver on a 15 minute interval using Openweather's API and weather station.  It can additionally format city dimension data to give context about Vancouver on a no-scheduled, trigger basis.  Finally, weather data is uploaded to S3 so that data scientists with permissions can work with the data using tools like Spark on EMR or Glue.  It is an example of performing an ETL on a schedule and formatting both fact and dimension data for respective use cases.  This project is named after Susanoo, the Japanese storm god in Shinto religion.

# JSON data
The normal HTTP response from Openweather's API is like such:
```json
{
    "coord": {
        "lon": -123.1193,
        "lat": 49.2497
    },
    "weather": [
        {
            "id": 804,
            "main": "Clouds",
            "description": "overcast clouds",
            "icon": "04d"
        }
    ],
    "base": "stations",
    "main": {
        "temp": 287.05,
        "feels_like": 286.48,
        "temp_min": 284.94,
        "temp_max": 288.7,
        "pressure": 1012,
        "humidity": 76,
        "sea_level": 1012,
        "grnd_level": 1004
    },
    "visibility": 10000,
    "wind": {
        "speed": 2.68,
        "deg": 243,
        "gust": 4.02
    },
    "clouds": {
        "all": 100
    },
    "dt": 1728001716,
    "sys": {
        "type": 2,
        "id": 2011597,
        "country": "CA",
        "sunrise": 1727964954,
        "sunset": 1728006389
    },
    "timezone": -25200,
    "id": 6173331,
    "name": "Vancouver",
    "cod": 200
}
```
Reformatting this into fact data makes it organized and easier to understand for data science, and looks like such:
```json
{
    "city": "Vancouver",
    "country": "CA",
    "base": "stations",
    "description": "mist",
    "time": "2024-10-04 09:20:59",
    "temperature": 10.59,
    "min_temp": 9.98,
    "max_temp": 11.57,
    "pressure": 1007,
    "humidity": 91,
    "visibility": 9656,
    "wind_speed": 5.14,
    "wind_deg": 110
}
```
The first four JSON attributes give context to the weather data (city, country, base, description)
and the last 9 attributes are pure fact data.

Fact data can be used for data scientists interested in learning about the climate in Vancouver.  If this program were to run on a server for years recording fact data, data scientists could also use it to find insights on climate change and it's impact to the city.

Dimension data is also created that gives context to Vancouver city.  It looks like this:
```json
{
    "city": "Vancouver",
    "country": "CA",
    "longitude": -123.1193,
    "latitude": 49.2497,
    "timezone": -25200
}
```
Because the dimension data is static and not long thought to change (unless the city or the country change their names), the DAG responsible for fetching the data only does this on a triggered basis and there is no schedule for updating the city_dimensions.json file where the dimension data is stored.

# Running the program
If you have airflow on your linux or mac, you can first `cd` into the project directory and run the bash command
`airflow db init`
This will create your airflow project.

You can then start the webserver using a shell script or running these commmands in your terminal:

`export AIRFLOW_HOME=$(pwd)`

`airflow scheduler & airflow webserver -p 8080`

Try running the openweather_current_dag and notice the weather updates without you having to trigger it.

You can also try triggering the city_dimensions_dag and it will create or update the dimension data
