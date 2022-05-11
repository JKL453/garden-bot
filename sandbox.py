from yr.libyr import Yr

weather = Yr(location_name='Tyskland/Schleswig-Holstein/Lübeck')

for forecast in weather.forecast(as_json=True):
    print(forecast)

    "data":{
        "instant":{
            "details":{
                "air_pressure_at_sea_level":1024.8,
                "air_temperature":1.6,
                "cloud_area_fraction":98.6,
                "relative_humidity":65.9,
                "wind_from_direction":52.3,
                "wind_speed":1.4}},"next_12_hours":{"summary":{"symbol_code":"clearsky_night"}},"next_1_hours":{"summary":{"symbol_code":"cloudy"},"details":{"precipitation_amount":0.0}},"next_6_hours":{"summary":{"symbol_code":"clearsky_night"},"details":{"precipitation_amount":0.0}}}},{"time":"2022-03-05T17:00:00Z",