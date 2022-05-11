from modules.config import UA_SITENAME
import requests
import json

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


    def get_forecast(self) -> dict:
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
        forecast_data_json = json.loads(response.text)
        #print(json.dumps(response_json, indent=4))

        return forecast_data_json
        

    # To be implemented:
    # def get_forecast_for_day(self, today):

    # https://developer.yr.no/doc/ForecastJSON/


    """def get_forecast(self):
        self.forecast_data['data'] = [{ 'from': forecast['@from'], 
                                        'to': forecast['@to'], 
                                        'temperature': float(forecast['temperature']['@value']), 
                                        'rain': float(forecast['precipitation']['@value'])} 
                             for forecast in self.weather_data.forecast()]

        return self.forecast_data"""

    """def get_temperature(self):
        return self.weather.temperature

    def get_wind(self):
        return self.weather.wind_speed

    def get_humidity(self):
        return self.weather.humidity

    def get_pressure(self):
        return self.weather.pressure

    def get_sunrise(self):
        return self.weather.sunrise

    def get_sunset(self):
        return self.weather.sunset

    def get_forecast(self):
        return self.weather.forecast
"""