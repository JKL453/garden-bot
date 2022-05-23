from modules.config import UA_SITENAME
import requests
import json
import datetime, pytz

class WeatherReport(object):
    """
    Requests the weather forecast via yr.no API.
    """
    
    def __init__(self, location, date):
        """
        Set location and time of current weather report.
        """

        # location = [lat, lon, alt]
        # date = datetime object
        self.lat = location[0]
        self.lon = location[1]
        self.alt = location[2]
        self.date = date


    def get_weather_data(self) -> json:
        """
        Returns the forecast data as a dictionary.
        """
        
        # create forecast URL for given location
        self.base_url = 'https://api.met.no/weatherapi/locationforecast/2.0/compact?'
        self.api_url = '{base_url}lat={lat}&lon={lon}&altitude={alt}'.format(
            base_url=self.base_url,
            lat=self.lat,
            lon=self.lon,
            alt=self.alt
        )

        # create user agent for API call
        self.sitename = UA_SITENAME
        self.headers = {'User-Agent': self.sitename}

        # send request to YR API
        response = requests.get(self.api_url, headers=self.headers)

        # convert response to JSON
        self.response_json = json.loads(response.text)
        self.weather_data = json.dumps(self.response_json, indent=4)

        return self.weather_data


    def get_weather_from_time(self, datetime_object):
        """
        Get weather data for a certain period of time
        :param string time: time of weather forecast
        :return: weather data
        """
        time_string = datetime.datetime.strftime(datetime_object, '%Y-%m-%dT%H:00:00Z')
        print(time_string)

        for item in self.response_json['properties']['timeseries']:
            if item['time'] == time_string:
                return json.dumps(item['data'], indent=4)
        

    # To be implemented:
    # def get_forecast_for_day(self, today):,

    # https://developer.yr.no/doc/ForecastJSON/

    # weather_report = WeatherReport(location=location, date=date)
    # forecast = weather_report.get_forecast(time=time)
    # weather_symbol = forecast.get_weather_symbol()
    
