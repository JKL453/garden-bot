from time import strftime
from modules.YrUtils import WeatherReport
from datetime import datetime as dt 
import pytz
import json
import locale

lat = 53.86893
lon = 10.68729
alt = 162

location = [lat, lon, alt]
time_now = dt.now(pytz.timezone("Europe/Berlin"))

weather_report = WeatherReport(location=location, date=time_now)
forecast = weather_report.get_weather_data()

# print prettified json forecast
#print(json.dumps(forecast, indent=4))

weather_now = weather_report.get_weather_from_time(time_now, return_repr='json')
print("")
print(time_now)
print("")
#print(weather_now)
print(weather_now['next_6_hours'])
print(type(weather_now))
print('\n\n')
# add args for length of prediction period
# weather_next_hour = weather_report.get_weather_from_time(date=date, prediction_period=1)

# get dates for tomorrow and day after tomorrow
date_tomorrow, date_after_tomorrow = WeatherReport.get_next_dates()
#print(str(tomorrow_date) + ' and ' + str(day_after_tomorrow_date))

# test: get multiple reports
weather_tomorrow = weather_report.get_weather_from_time(date_tomorrow, return_repr='str')
#print(weather_tomorrow)
weather_after_tomorrow = weather_report.get_weather_from_time(date_after_tomorrow, return_repr='str')
#print(weather_after_tomorrow)

def create_daily_forecast(date) -> str:
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
    weather_data_06 = weather_report.get_weather_from_time(date_06, return_repr='json')
    date_12 = date.replace(hour=12, minute=0)
    weather_data_12 = weather_report.get_weather_from_time(date_12, return_repr='json')
    date_18 = date.replace(hour=18, minute=0)
    weather_data_18 = weather_report.get_weather_from_time(date_18, return_repr='json')

    date_06_uv = date.replace(hour=9, minute=0)
    weather_data_06_uv = weather_report.get_weather_from_time(date_06_uv, return_repr='json')

    temp_min_06 = int(weather_data_06['next_6_hours']['details']['air_temperature_min'])
    temp_max_06 = int(weather_data_06['next_6_hours']['details']['air_temperature_max'])
    temp_min_12 = int(weather_data_12['next_6_hours']['details']['air_temperature_min'])
    temp_max_12 = int(weather_data_12['next_6_hours']['details']['air_temperature_max'])
    temp_min_18 = int(weather_data_18['next_6_hours']['details']['air_temperature_min'])
    temp_max_18 = int(weather_data_18['next_6_hours']['details']['air_temperature_max'])

    rain_mm_06 = weather_data_06['next_6_hours']['details']['precipitation_amount']
    rain_mm_12 = weather_data_12['next_6_hours']['details']['precipitation_amount']
    rain_mm_18 = weather_data_18['next_6_hours']['details']['precipitation_amount']

    rain_prob_06 = weather_data_06['next_6_hours']['details']['probability_of_precipitation']
    rain_prob_12 = weather_data_12['next_6_hours']['details']['probability_of_precipitation']
    rain_prob_18 = weather_data_18['next_6_hours']['details']['probability_of_precipitation']

    uv_data = get_uv_data(date)

    weather_msg = ''
    weather_msg += 'Wetter für ' + dt.strftime(date, '%A')
    weather_msg += ', den ' + str(date.day) + '.' + str(date.month) + '.' + str(date.year) + ': \n\n'

    
    weather_msg += '06 bis 12 Uhr' + '\n'
    #weather_msg += 'Temperatur      Niederschlag' + '\n'
    weather_msg += '{}°C - {}°C'.format(temp_min_06, temp_max_06)
    weather_msg += '     '
    weather_msg += '{} mm ({}%)'.format(rain_mm_06, rain_prob_06)
    weather_msg += '     '
    weather_msg += 'UV max: {}'.format(uv_data[1])
    weather_msg += '\n\n'

    weather_msg += '12 bis 18 Uhr' + '\n'
    #weather_msg += 'Temperatur      Niederschlag' + '\n'
    weather_msg += '{}°C - {}°C'.format(temp_min_12, temp_max_12)
    weather_msg += '     '
    weather_msg += '{} mm ({}%)'.format(rain_mm_12, rain_prob_12)
    weather_msg += '     '
    weather_msg += 'UV max: {}'.format(uv_data[3])
    weather_msg += '\n\n'

    weather_msg += '18 bis 24 Uhr' + '\n'
    #weather_msg += 'Temperatur      Niederschlag' + '\n'
    weather_msg += '{}°C - {}°C'.format(temp_min_18, temp_max_18)
    weather_msg += '     '
    weather_msg += '{} mm ({}%)'.format(rain_mm_18, rain_prob_18)
    weather_msg += '     '
    weather_msg += 'UV max: {}'.format(uv_data[5])
    weather_msg += '\n\n'
 
    return weather_msg

def get_uv_data(date) -> list:
    """
    Get UV-Index for a given date
    :param datetime date: datetime object
    :return: UV-Index
    """
    uv_06_12 = []
    for time in range(6, 12):
        date_06_12 = date.replace(hour=time, minute=0)
        weather_data_06_12 = weather_report.get_weather_from_time(date_06_12, return_repr='json')
        uv_06_12.append(weather_data_06_12['instant']['details']['ultraviolet_index_clear_sky'])

    uv_12_18 = []
    for time in range(12, 18):
        date_12_18 = date.replace(hour=time, minute=0)
        weather_data_12_18 = weather_report.get_weather_from_time(date_12_18, return_repr='json')
        uv_12_18.append(weather_data_12_18['instant']['details']['ultraviolet_index_clear_sky'])

    uv_18_24 = []
    for time in range(18, 24):
        date_18_24 = date.replace(hour=time, minute=0)
        weather_data_18_24 = weather_report.get_weather_from_time(date_18_24, return_repr='json')
        uv_18_24.append(weather_data_18_24['instant']['details']['ultraviolet_index_clear_sky'])
    
    return [min(uv_06_12), max(uv_06_12), min(uv_12_18), max(uv_12_18), min(uv_18_24), max(uv_18_24)]

weather_msg = create_daily_forecast(date_tomorrow)
print(weather_msg)