# Introduction
There are three distinct git branches, each with different local and cloud data formats.  The structure of each branch is shown in the table below:

| Branch Name | Local Data Format | Cloud Storage Type  |
| ------------- | ------------- | ------------- |
| json  | JSON  | JSON in an S3 bucket  |
| csv  | CSV  | gsheets on Google Drive  |
| sql  | postgreSQL  | Snowflake Data Warehouse  |

# How specifically this branch works
## Calling Openweather's API's and reorganizing data
The normal HTTP response from Openweather's API provided with a given city, country, and an API key returns JSON data like such:
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
JSON deserialization is performed to transform the weather data into a more refined JSON format, making it decluttered, and easier to understand for data science, and looks like such:
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
The first four attributes give context to the weather data (city, country, base, description)
and the last 9 are purely fact data (data that holds quantitative metrics about weather events).

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

To get pollution data from Openweather, there is another API endpoint to use that gives a different HTTP response.  The documentation is here: https://openweathermap.org/api/air-pollution.  The endpoint requires latitude and longitude parameters and so uses the city data we created.  There is no way to get pollution data using city name and country.

```json
{
  "coord":[
    50,
    50
  ],
  "list":[
    {
      "dt":1605182400,
      "main":{
        "aqi":1
      },
      "components":{
        "co":201.94053649902344,
        "no":0.01877197064459324,
        "no2":0.7711350917816162,
        "o3":68.66455078125,
        "so2":0.6407499313354492,
        "pm2_5":0.5,
        "pm10":0.540438711643219,
        "nh3":0.12369127571582794
      }
    }
  ]
}
```

For pollution data the refined JSON format looks like such:
```json
{
    "city": "Vancouver",
    "country": "CA",
    "time": "2026-01-14 23:16:50",
    "AQI": 1,
    "CO": 203.53,
    "NO": 0.44,
    "NO2": 12,
    "O3": 21.69,
    "SO2": 1.21,
    "PM2_5": 3.58,
    "PM10": 4.49,
    "NH3": 0.23
}
```