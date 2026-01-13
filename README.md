# Introduction
Susanoo is a data engineering project that explores the different formats data can be stored on the cloud.  It retrieves pollution and weather data from Openweather using their API and is transformed and uploaded to the cloud.  There are three git branches where data is stored locally in different formats and then uploaded to certain cloud sources as shown in this table:

| Branch Name | Local Data Format | Cloud Storage Type  |
| ------------- | ------------- | ------------- |
| json  | JSON  | S3 bucket  |
| csv  | CSV  | gsheets on Google Drive  |
| sql  | postgreSQL  | Snowflake Data Warehouse  |

Data scientists with permissions can work with the data using tools like Spark on EMR or Glue in S3, or use SQL in Snowflake.  For non-techincal end-users who aren't familiar with AWS or Snowflake it is possible to read the data in gsheets.  Susanoo is an example of performing ETL's on a schedule and formatting fact and dimension data for respective use cases.  This project is a sister project to Akashi.  Whereas Akashi is a full-scale data engineering + analytics project with stock graphs for end users, Akashi is a purely data engineering project that explores the many ways data can be formatted and stored on the cloud.  It is named after Susanoo, the Japanese storm god in Shinto religion.

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

Fact data can be used for data scientists interested in learning about the climate in the specific city.  If this program were to run on a server for years recording fact data, data scientists could also use it to find insights on climate change and it's impact to the city.

Dimension data is also created that gives context to the city.  It looks like this:
```json
{
    "city": "Vancouver",
    "country": "CA",
    "longitude": -123.1193,
    "latitude": 49.2497,
    "timezone": -25200
}
```
Because the dimension data about a city is static and not thought to change (unless the city or the country change their names), the DAG responsible for fetching this type of data is not on a schedule for updating cities

# Running the program
If you have airflow on your linux or mac, you can first `cd` into the project directory and run the bash command
`airflow db init`
This will create your airflow project.

You can then start the webserver using a shell script or running these commmands in your terminal:

`export AIRFLOW_HOME=$(pwd)`

`airflow scheduler & airflow webserver -p 8080`

Try running the openweather_current_dag and notice the weather updates without you having to trigger it.

You can also try triggering the city_dimensions_dag and it will create or update the dimension data
