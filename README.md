# Introduction
Susanoo is a data engineering project that explores the different formats data can be stored as.  It retrieves pollution and weather data for different cities on the west coast using Openweather's API.  It then transforms the data and then uploads it to the cloud.  There are three distinct git branches, each with different local and cloud data formats and even tailored README files for these specific data formats.  The structure of each branch is shown in the table below:

| Branch Name | Local Data Format | Cloud Storage Type  |
| ------------- | ------------- | ------------- |
| json  | JSON  | JSON in an S3 bucket  |
| csv  | CSV  | gsheets on Google Drive  |
| sql  | postgreSQL  | Snowflake Data Warehouse  |

Susanoo is an example of performing ETL's on a schedule and formatting fact and dimension data for respective use cases.  This project is a sister project to Akashi.  Whereas Akashi is a full-scale data engineering + analytics project with stock graphs for end users, Akashi is a purely data engineering project that explores the many ways data can be formatted and stored.  It is named after Susanoo, the Japanese storm god in Shinto religion.

# Calling Openweather's API's and reorganizing data
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
JSON deserialization is performed to transform the weather data into a tabular format, making it organized, decluttered, and easier to understand for data science, and looks like such:
|city     |country|base    |description  |time               |temperature|temp_min|temp_max|pressure|humidity|visibility|wind_speed|wind_deg|
|---------|-------|--------|-------------|-------------------|-----------|--------|--------|--------|--------|----------|----------|--------|
|Vancouver|CA     |stations|broken clouds|2025-03-29 15:29:48|10.18      |9.57    |10.71   |1018    |74      |10000     |4.47      |20      |
|Vancouver|CA     |stations|broken clouds|2025-03-29 15:38:00|10.18      |9.3     |10.58   |1018    |73      |10000     |4.92      |17      |
|Vancouver|CA     |stations|broken clouds|2025-03-29 15:51:01|10.36      |9.57    |10.72   |1018    |73      |10000     |4.92      |18      |

The first four columns give context to the weather data (city, country, base, description)
and the last 9 are purely fact data (data that holds quantitative metrics about weather events).

Dimension data is also created that gives context to the city.  It looks like this:
|city     |country|latitude|longitude    |timezone           |
|---------|-------|--------|-------------|-------------------|
|Los Angeles|US     |-118.2437|34.0522      |-25200             |
|San Francisco|US     |-122.4194|37.7749      |-25200             |
|Vancouver|CA     |-123.1155|49.2624      |-25200             |

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

For pollution data the tabular format looks like such:
|city     |country|time    |aqi          |co                 |no  |no2  |o3    |so2 |pm2_5|pm10 |nh3 |
|---------|-------|--------|-------------|-------------------|----|-----|------|----|-----|-----|----|
|Vancouver|CA     |2025-03-29 15:48:06|1            |323.77             |1.54|12.17|57.94 |4.29|2.8  |4.92 |1.76|

# Scheduling of DAGs
The DAG responsible for fetching weather data is scheduled to run every 15 minutes.  This is sufficient to provide historical data that can be analyzed.  Real-time weather data from XWeather could be collected with Kafka, however for a study of historical data this is overkill and will require a lot of storage, let alone the monthly cost for an API subscription.

The DAG responsible for fetching pollution data is scheduled to run every hour but could easily be changed to every 10 or 15 minutes.  One thing to consider when regularly collecting data from Openweather is the API limit of 1000 calls/day.  For 5 cities, you can collect weather and pollution data every 15 minutes with 40 calls leftover at the end of the day.

Because the dimension data about a city is essentially static (A city's name, country, and timezone rarely changes), the DAG responsible for fetching this type of data is trigger-based and not on a schedule.

# On the applications for data scientists
Weather data can be used for data scientists interested in learning about the climate in the specific city.  If this program were to run on a server for years recording weather data, data scientists could also use it to find insights on climate change and it's impact to each city.  Additionally, comparisons of the impact of climate change between different cities could also be studied.  Data scientists can also join the weather data with other datasets.  For example, if a data scientist had a dataset about traffic accidents in Vancouver, they could join the two datasets on city and country to see if there is any correlation between weather events and traffic accidents.

This open-source project does not record data for years due to the hourly cost of running an EC2 server, however an EC2 server with airflow installed was run for a few days collecting data before being shut down.  The point is, the project can be put into production if funded to serve data scientists interested in studying climate change and pollution.

# Missing values and the limits of pandas backfilling
When it comes to data cleaning, backfilling is the usual answer.  However, when collecting pollution data about LA for a few hours, there were often consecutive NaN values which means that backfilling won't work.  Setting these values to 0 will also affect a machine learning algorithm.  A data scientist could choose to not use a column with missing values for machine learning but will miss out on dimensionality.  There is a tradeoff however you go about it.  One area that is not as greatly affected is data visualization which will still work and not lose performance when values are 0.

# On the comparison of data formats
Data scientists with permissions can work with the JSON in S3 buckets using tools like Spark on EMR or Glue. In a way, Spark makes it easy to work with many formats of data including JSON.  However, storing data in S3 as a parquet file has the best compression and performance and should be considered if seriously using Spark to work with a data lake.  The pandas library has a method to convert a dataframe into parquet and upload to AWS.

gsheets is a nice and easy way for non-technical users to examine the data collected without getting their hands dirty with AWS or Snowflake.  You can access the gsheet for this project here: https://docs.google.com/spreadsheets/d/1H2te8n_4auKfRCbmduC-hwm2GQgudOs9J5JwA1L_SyY/edit?usp=drive_link.  There are also data visualization tools for non-technical users in gsheets.  However, for more advanced programming like time series forecasting, gsheets is not a viable option as it is not compatible with python libraries like pandas, scikit-learn or tensorflow that are needed.  When running airflow to upload weather data periodically, gsheets was quick to update the values.

SQL provides the fastest retrieval of data both locally and in a data warehouse.  It is even faster than reading data from CSV files.  It's not so intimidating to access data from a postgres database as you can actually use pandas to load SQL data into memory.  The Snowflake data warehouse is an extension of the local database and was used to globalize the data for use of a team project.  If you're processing data with the SQL language and for the fastest processing time, SQL databases and data warehouses are the way to go.

# Running the program
If you have airflow on your linux or mac, you can first `cd` into the project directory and run the bash command
`airflow db init`
This will create your airflow project.

You can then start the webserver using a shell script or running these commmands in your terminal:

`export AIRFLOW_HOME=$(pwd)`

`airflow scheduler & airflow webserver -p 8080`

Try turning on the vancouver_weather_etl and notice the weather updates without you having to trigger it.

You can also try triggering the city_etl DAG and it will create or update the cities table in postgres