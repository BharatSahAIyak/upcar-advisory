import requests

def get_weather(station_id):
    weather_data={}

    url1 = f"https://city-imd-gov.uat.bhasai.samagra.io/api/current_wx_api.php?id={station_id}"
    url2 = f"https://city.imd.gov.in/api/cityweather.php?id={station_id}"

    # Make a GET request to the API
    res1 = requests.get(url1)
    res2 = requests.get(url1)

    # Check if the request was successful
    if res1.status_code == 200:
        data = res1.json()

        weather_data={
            "rainfallInMM": data['Past_24_hrs_Rainfall'],
            "maximumTemperatureInDegrees": data['Todays_Forecast_Max_Temp'],
            "minimumTemperatureInDegrees": data['Todays_Forecast_Min_temp'],
            "relativeHumidity": data['Relative_Humidity_at_1730'],
            "windSpeedInKMPH": 6,
            "windDirectionInDegrees": 202,
            "cloudCoverInOkta": 4
        }

    else:
        print(f"Failed to get data from API. Status code: {res1.status_code}")

    if res2.status_code == 200:
        data = res2.json()

        weather_data["windSpeedInKMPH"]=data["Wind Speed KMPH"]
        weather_data["windDirectionInDegrees"]=data["Wind Direction"]
        weather_data["cloudCoverInOkta"]=data["Nebulosity"]
        
    else:
        print(f"Failed to get data from API. Status code: {res2.status_code}")