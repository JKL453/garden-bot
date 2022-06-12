from modules.config import UA_SITENAME
import requests
import json
from datetime import datetime as dt
from datetime import timedelta
import pytz
import locale

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


    def weather_from_time(self, datetime_object, return_repr='json'):
        """
        Get weather data for a certain period of time
        :param string time: time of weather forecast
        :return: weather data
        """
        time_string = dt.strftime(datetime_object, '%Y-%m-%dT%H:00:00Z')
        #print(dt

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
        date_tomorrow = dt.now(pytz.timezone("Europe/Berlin")) + timedelta(days=1)
        date_tomorrow = date_tomorrow.replace(hour=6, minute=0)
        date_after_tomorrow= dt.now(pytz.timezone("Europe/Berlin")) + timedelta(days=2)
        date_after_tomorrow = date_after_tomorrow.replace(hour=6, minute=0)
        return date_tomorrow, date_after_tomorrow

    def get_uni_code(self, yr_symbol_code):
        search_name = yr_symbol_code
        for uni_name, yr_name_list in self.weather_symbols_yr_names.items():
            for yr_name in range(len(yr_name_list)):
                if yr_name_list[yr_name] == search_name:
                    uni_code = self.weather_symbols_uni[uni_name]
                    return uni_code

    def daily_forecast(self, date) -> str:
        """
        Create a weather message for a certain time period
        :param datetime date: datetime object
        :param int period: number of hours to predict
        :return: weather message
        """

        # set locale to German language
        locale.setlocale(locale.LC_TIME, "de_DE")

        # get weather data for given time periods
        date_06 = date.replace(hour=6, minute=0)
        weather_data_06 = self.weather_from_time(date_06, return_repr='json')
        date_12 = date.replace(hour=12, minute=0)
        weather_data_12 = self.weather_from_time(date_12, return_repr='json')
        date_18 = date.replace(hour=18, minute=0)
        weather_data_18 = self.weather_from_time(date_18, return_repr='json')

        date_06_uv = date.replace(hour=9, minute=0)
        weather_data_06_uv = self.weather_from_time(date_06_uv, return_repr='json')

        temp_min_06 = int(weather_data_06['next_6_hours']['details']['air_temperature_min'])
        temp_max_06 = int(weather_data_06['next_6_hours']['details']['air_temperature_max'])
        temp_min_12 = int(weather_data_12['next_6_hours']['details']['air_temperature_min'])
        temp_max_12 = int(weather_data_12['next_6_hours']['details']['air_temperature_max'])
        temp_min_18 = int(weather_data_18['next_6_hours']['details']['air_temperature_min'])
        temp_max_18 = int(weather_data_18['next_6_hours']['details']['air_temperature_max'])

        rain_min_mm_06 = weather_data_06['next_6_hours']['details']['precipitation_amount_min']
        rain_max_mm_06 = weather_data_06['next_6_hours']['details']['precipitation_amount_max']
        rain_min_mm_12 = weather_data_12['next_6_hours']['details']['precipitation_amount_min']
        rain_max_mm_12 = weather_data_12['next_6_hours']['details']['precipitation_amount_max']
        rain_min_mm_18 = weather_data_18['next_6_hours']['details']['precipitation_amount_min']
        rain_max_mm_18 = weather_data_18['next_6_hours']['details']['precipitation_amount_max']

        rain_prob_06 = weather_data_06['next_6_hours']['details']['probability_of_precipitation']
        rain_prob_12 = weather_data_12['next_6_hours']['details']['probability_of_precipitation']
        rain_prob_18 = weather_data_18['next_6_hours']['details']['probability_of_precipitation']

        yr_symbol_code_06 = weather_data_06['next_6_hours']['summary']['symbol_code']
        weather_symbol_06 = self.get_uni_code(yr_symbol_code_06)

        yr_symbol_code_12 = weather_data_12['next_6_hours']['summary']['symbol_code']
        weather_symbol_12 = self.get_uni_code(yr_symbol_code_12)

        yr_symbol_code_18 = weather_data_18['next_6_hours']['summary']['symbol_code']
        weather_symbol_18 = self.get_uni_code(yr_symbol_code_18)

        uv_data = self.get_uv_data(date)

        weather_msg = ''
        weather_msg += 'Wetter für ' + dt.strftime(date, '%A')
        weather_msg += ', den ' + str(date.day) + '.' + str(date.month) + '.' + str(date.year) + ': \n\n'


        weather_msg += '06 bis 12 Uhr' + '   ' + weather_symbol_06 + '\n'
        #weather_msg += 'Temperatur      Niederschlag' + '\n'
        weather_msg += '{}°C - {}°C'.format(temp_min_06, temp_max_06)
        weather_msg += '     '
        weather_msg += '{} mm - {} mm ({}%)'.format(rain_min_mm_06, rain_max_mm_06, rain_prob_06)
        weather_msg += '     '
        weather_msg += 'UV max: {}'.format(uv_data[1])
        weather_msg += '\n\n'

        weather_msg += '12 bis 18 Uhr' + '   ' + weather_symbol_12 + '\n'
        #weather_msg += 'Temperatur      Niederschlag' + '\n'
        weather_msg += '{}°C - {}°C'.format(temp_min_12, temp_max_12)
        weather_msg += '     '
        weather_msg += '{} mm - {} mm ({}%)'.format(rain_min_mm_12, rain_max_mm_12, rain_prob_12)
        weather_msg += '     '
        weather_msg += 'UV max: {}'.format(uv_data[3])
        weather_msg += '\n\n'

        weather_msg += '18 bis 24 Uhr' + '   ' + weather_symbol_18 + '\n'
        #weather_msg += 'Temperatur      Niederschlag' + '\n'
        weather_msg += '{}°C - {}°C'.format(temp_min_18, temp_max_18)
        weather_msg += '     '
        weather_msg += '{} mm - {} mm ({}%)'.format(rain_min_mm_18, rain_max_mm_18, rain_prob_18)
        weather_msg += '     '
        weather_msg += 'UV max: {}'.format(uv_data[5])
        weather_msg += '\n\n'
    
        return weather_msg

    def get_uv_data(self, date) -> list:
        """
        Get UV-Index for a given date
        :param datetime date: datetime object
        :return: UV-Index
        """
        uv_06_12 = []
        for time in range(6, 12):
            date_06_12 = date.replace(hour=time, minute=0)
            weather_data_06_12 = self.weather_from_time(date_06_12, return_repr='json')
            uv_06_12.append(weather_data_06_12['instant']['details']['ultraviolet_index_clear_sky'])

        uv_12_18 = []
        for time in range(12, 18):
            date_12_18 = date.replace(hour=time, minute=0)
            weather_data_12_18 = self.weather_from_time(date_12_18, return_repr='json')
            uv_12_18.append(weather_data_12_18['instant']['details']['ultraviolet_index_clear_sky'])

        uv_18_24 = []
        for time in range(18, 24):
            date_18_24 = date.replace(hour=time, minute=0)
            weather_data_18_24 = self.weather_from_time(date_18_24, return_repr='json')
            uv_18_24.append(weather_data_18_24['instant']['details']['ultraviolet_index_clear_sky'])

        return [min(uv_06_12), max(uv_06_12), min(uv_12_18), max(uv_12_18), min(uv_18_24), max(uv_18_24)]
    
    # To be implemented:
    # def get_forecast_for_day(self, today):,

    # https://developer.yr.no/doc/ForecastJSON/

    # weather_report = WeatherReport(location=location, date=date)
    # forecast = weather_report.get_forecast(time=time)
    # weather_symbol = forecast.get_weather_symbol()
    