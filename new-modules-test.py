"""from telegram import Location

import datetime, pytz
from modules import WeatherReport as wr
from config import MY_LOCATION

# Specify timezone and create a datetime object
my_timezone = pytz.timezone("Europe/Berlin")
my_date = datetime.datetime.now(my_timezone)

weather_report = wr.WeatherReport(location = MY_LOCATION, date= my_date)"""

from modules.YrUtils import WeatherReport as wr
import datetime, pytz
import json

lat = 53.86893
lon = 10.68729
alt = 162

location = [lat, lon, alt]
date = datetime.datetime.now(pytz.timezone("Europe/Berlin"))

weather_report = wr(location=location, date=date)
forecast = weather_report.get_forecast()
print(json.dumps(forecast, indent=4))