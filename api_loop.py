import openmeteo_requests
import requests_cache
import pandas as pd
import time
from retry_requests import retry
from typing import Dict, Any

class WeatherData:
    def __init__(self, latitude: float, longitude: float, forecast_hours: int = 6, timezone: str = "Europe/Berlin") -> None:
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.forecast_hours: int = forecast_hours
        self.timezone: str = timezone

        # Setup für die API-Anfragen
        self.cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)

    def fetch_weather(self) -> pd.DataFrame:
        """Ruft die Wettervorhersage für die nächsten forecast_hours ab."""
        # API-Parameter für eine Vorhersage über die nächsten Stunden
        params: Dict[str, Any] = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability", "precipitation", "cloud_cover", "wind_speed_10m"],
            "timezone": self.timezone,
            "forecast_hours": self.forecast_hours  # Wettervorhersage für die nächsten 6 Stunden
        }

        # API-Anfrage
        response = self.openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)[0]
        
        # Stündliche Wetterdaten extrahieren
        hourly = response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
            "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
            "precipitation_probability": hourly.Variables(2).ValuesAsNumpy(),
            "precipitation": hourly.Variables(3).ValuesAsNumpy(),
            "cloud_cover": hourly.Variables(4).ValuesAsNumpy(),
            "wind_speed_10m": hourly.Variables(5).ValuesAsNumpy()
        }

        return pd.DataFrame(hourly_data)

    def save_forecast(self, forecast_df: pd.DataFrame) -> None:
        """Speichert die stündliche Vorhersage in einer CSV-Datei."""
        forecast_df.to_csv("6_hour_forecast.csv", index=False)
        print("6-hour forecast saved to '6_hour_forecast.csv'")

# Nutzung der Klasse in einer Endlosschleife
latitude = 50.935173  # Köln
longitude = 6.95310
forecast_hours = 6  # Vorhersage für die nächsten 6 Stunden

weather = WeatherData(latitude, longitude, forecast_hours)

while True:
    # Abruf der 6-Stunden-Wettervorhersage
    forecast_df = weather.fetch_weather()
    weather.save_forecast(forecast_df)
    
    # Warte 6 Stunden, bevor die nächste Abfrage erfolgt
    time.sleep(6 * 60 * 60)  # 6 Stunden in Sekunden
