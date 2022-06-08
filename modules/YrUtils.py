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

        # uni code weather symbols
        # https://unicode.org/emoji/charts/full-emoji-list.html
        self.weather_symbols_uni = {
            'sun': '\U00002600',
            'cloud': '\U00002601',
            'sun behind cloud': '\U000026C5',
            'cloud with lightning and rain': '\U000026C8',
            'sun behind small cloud': '\U0001F324',
            'sun behind large cloud': '\U0000F325',
            'sun behind rain cloud ': '\U0001F326',
            'cloud with rain': '\U0001F327',
            'cloud with snow': '\U0001F328',
            'cloud with lightning': '\U0001F329',
            'tornado': '\U0001F32A',
            'fog': '\U0001F32B',
            'wind face': '\U0001F32C'
        }

        # yr weather symbols numbers
        # https://github.com/nrkno/yr-weather-symbols
        self.weather_symbols_yr_numbers = {
            'sun':  ['01'],
            'cloud': ['04'],
            'sun behind cloud': ['03'],
            'cloud with lightning and rain': ['06', '24', '25', '26', '20', '27'],
            'sun behind small cloud': ['02'],
            'sun behind large cloud': [],
            'sun behind rain cloud ': ['40', '05', '41', '42', '07', '43'],
            'cloud with rain': ['46', '09', '10'],
            'cloud with snow': ['44', '08', '45', '28', '21', '29', '47', '12', '48', '49', '13', '50'],
            'cloud with lightning': ['30', '22', '11', '31', '23', '32', '33', '14', '34'],
            'fog': ['15']
        }

        # yr weather symbols names
        # https://github.com/nrkno/yr-weather-symbols
        self.weather_symbols_yr_names = {
            'sun':  ['clearsky_day',
                     'clearsky_night'],
            'cloud': ['cloudy'],
            'sun behind cloud': ['partlycloudy_day',
                                 'partlycloudy_night'],
            'cloud with lightning and rain': ['lightrainshowersandthunder_day',
                                              'lightrainshowersandthunder_night',
                                              'rainshowersandthunder_day',
                                              'rainshowersandthunder_night',
                                              'heavyrainshowersandthunder_day',
                                              'heavyrainshowersandthunder_night'],
            'sun behind small cloud': ['fair_day',
                                       'fair_night'],
            'sun behind large cloud': [],
            'sun behind rain cloud ': ['lightrainshowers_day',
                                       'lightrainshowers_night',
                                       'rainshowers_day',
                                       'rainshowers_night',
                                       'heavyrainshowers_day',
                                       'heavyrainshowers_night'],
            'cloud with rain': ['rain',
                                'heavyrain'],
            'cloud with snow': ['lightsnowshowers',
                                'snowshowers',
                                'heavysnowshowers',
                                'lightsnowshowersandthunder',
                                'snowshowersandthunder',
                                'heavysnowshowersandthunder',
                                'lightsleet',
                                'sleet',
                                'heavysleet',
                                'lightsnow',
                                'snow',
                                'heavysnow'],
            'cloud with lightning': ['lightrainandthunder',
                                     'rainandthunder',
                                     'heavyrainandthunder',
                                     'lightsleetandthunder',
                                     'sleetandthunder',
                                     'heavysleetandthunder',
                                     'lightsnowandthunder',
                                     'snowandthunder',
                                     'heavysnowandthunder'],
            'fog': ['fog']
        }

    def get_weather_data(self) -> json:
        """
        Returns the forecast data as a dictionary.
        """
        
        # create forecast URL for given location
        self.base_url = 'https://api.met.no/weatherapi/locationforecast/2.0/complete?'
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


    def get_weather_from_time(self, datetime_object, return_repr='json'):
        """
        Get weather data for a certain period of time
        :param string time: time of weather forecast
        :return: weather data
        """
        time_string = datetime.datetime.strftime(datetime_object, '%Y-%m-%dT%H:00:00Z')
        #print(time_string)

        for item in self.response_json['properties']['timeseries']:
            if item['time'] == time_string:
                if return_repr == 'str':
                    # this returns a prettified string
                    return json.dumps(item['data'], indent=4)
                if return_repr == 'json':
                    # this returns a dictionary
                    return item['data']
        
    def get_next_dates():
        """
        Get datetime objects for tomorrow and day after tomorrow
        :return: (datetime object, datetime object)
        """
        dt = datetime.datetime.now(pytz.timezone("Europe/Berlin")) + datetime.timedelta(days=1)
        date_tomorrow = dt.replace(hour=6, minute=0)
        dat= datetime.datetime.now(pytz.timezone("Europe/Berlin")) + datetime.timedelta(days=2)
        date_after_tomorrow = dat.replace(hour=6, minute=0)
        return date_tomorrow, date_after_tomorrow

    def get_uni_code(self, yr_symbol_code):
        search_name = yr_symbol_code
        for uni_name, yr_name_list in self.weather_symbols_yr_names.items():
            for yr_name in range(len(yr_name_list)):
                if yr_name_list[yr_name] == search_name:
                    uni_code = self.weather_symbols_uni[uni_name]
                    return uni_code

    # To be implemented:
    # def get_forecast_for_day(self, today):,

    # https://developer.yr.no/doc/ForecastJSON/

    # weather_report = WeatherReport(location=location, date=date)
    # forecast = weather_report.get_forecast(time=time)
    # weather_symbol = forecast.get_weather_symbol()
    