from modules.YrUtils import WeatherReport
import datetime, pytz
import json

lat = 53.86893
lon = 10.68729
alt = 162

location = [lat, lon, alt]
date = datetime.datetime.now(pytz.timezone("Europe/Berlin"))

weather_report = WeatherReport(location=location, date=date)
forecast = weather_report.get_forecast()

# print prettified json forecast
print(json.dumps(forecast, indent=4))