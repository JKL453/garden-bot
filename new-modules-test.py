from time import strftime
from modules.YrUtils import WeatherReport
from datetime import datetime as dt 
import pytz
import json

lat = 53.86893
lon = 10.68729
alt = 162

location = [lat, lon, alt]
time_now = dt.now(pytz.timezone("Europe/Berlin"))

weather_report = WeatherReport(location=location, date=time_now)
forecast = weather_report.get_weather_data()

# print prettified json forecast
#print(json.dumps(forecast, indent=4))

weather_now = weather_report.weather_from_time(time_now, return_repr='json')
print("")
print(time_now)
print("")
#print(weather_now)
print(weather_now['next_6_hours'])
print(type(weather_now))
print('\n\n')
# add args for length of prediction period
# weather_next_hour = weather_report.get_weather_from_time(date=date, prediction_period=1)

# get date for today

date = dt.now(pytz.timezone("Europe/Berlin"))
date_today  = date.replace(hour=6, minute=0)

# get dates for tomorrow and day after tomorrow
date_tomorrow, date_after_tomorrow = WeatherReport.get_next_dates()
#print(str(tomorrow_date) + ' and ' + str(day_after_tomorrow_date))

# test: get multiple reports
weather_tomorrow = weather_report.weather_from_time(date_tomorrow, return_repr='str')
#print(weather_tomorrow)
weather_after_tomorrow = weather_report.weather_from_time(date_after_tomorrow, return_repr='str')
#print(weather_after_tomorrow)

weather_msg = weather_report.daily_forecast(date_tomorrow)
print(weather_msg)