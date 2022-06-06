from time import strftime
from modules.YrUtils import WeatherReport
import datetime, pytz
import json
import locale

lat = 53.86893
lon = 10.68729
alt = 162

location = [lat, lon, alt]
time_now = datetime.datetime.now(pytz.timezone("Europe/Berlin"))

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

def create_daily_forecast(date):
    """
    Create a weather message for a certain time period
    :param datetime date: datetime object
    :param int period: number of hours to predict
    :return: weather message
    """
    locale.setlocale(locale.LC_TIME, "de_DE")
    weather_data = weather_report.get_weather_from_time(date, return_repr='json')

    weather_msg = ''
    weather_msg += 'Wetter für ' + datetime.datetime.strftime(date, '%A')
    weather_msg += ', den ' + str(date.day) + '.' + str(date.month) + '.' + str(date.year) + ':\n'
    weather_msg += 'Zeitraum' + 8*' ' + 'Temperatur' + '\n'
    weather_msg += '06 bis 12 Uhr' + '\n'
    weather_msg += '12 bis 18 Uhr' + '\n'
    weather_msg += '18 bis 24 Uhr' + '\n'

    weather_msg += 'Temperature: ' + str(weather_data['next_6_hours']['details']['air_temperature_max']) + '\n'
    return weather_msg

weather_msg = create_daily_forecast(date_tomorrow)
print('')
print(weather_msg)