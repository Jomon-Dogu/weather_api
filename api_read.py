import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from typing import Dict, Any

class WeatherData:
    def __init__(self, latitude: float, longitude: float, past_days: int, forecast_days: int = 3, timezone: str = "Europe/Berlin") -> None:
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.past_days: int = past_days
        self.forecast_days: int = forecast_days
        self.timezone: str = timezone

        # Setup für die API-Anfragen
        self.cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)

        # Die Parameter für die Anfrage
        self.params: Dict[str, Any] = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "rain", "showers", "snowfall", "cloud_cover", "wind_speed_10m"],
            "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability", "precipitation", "rain", "showers", "snowfall", "snow_depth", "cloud_cover", "wind_speed_10m"],
            "timezone": self.timezone,
            "past_days": self.past_days,
            "forecast_days": self.forecast_days
        }

        # API-Antworten
        self.responses: list = self.openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=self.params)

        # Initialisiere die Datenattribute
        self.current_data: Dict[str, Any] = {}
        self.hourly_data: Dict[str, Any] = {}

        self._process_data()

    def _process_data(self) -> None:
        """Verarbeitet die API-Antworten und speichert sie in Instanzvariablen."""
        response = self.responses[0]

        # Aktuelle Wetterdaten extrahieren
        self.current_data = {
            "time": response.Current().Time(),
            "temperature_2m": response.Current().Variables(0).Value(),
            "relative_humidity_2m": response.Current().Variables(1).Value(),
            "apparent_temperature": response.Current().Variables(2).Value(),
            "rain": response.Current().Variables(3).Value(),
            "showers": response.Current().Variables(4).Value(),
            "snowfall": response.Current().Variables(5).Value(),
            "cloud_cover": response.Current().Variables(6).Value(),
            "wind_speed_10m": response.Current().Variables(7).Value()
        }

        # Stündliche Wetterdaten extrahieren
        hourly = response.Hourly()
        self.hourly_data = {
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
            "rain": hourly.Variables(4).ValuesAsNumpy(),
            "showers": hourly.Variables(5).ValuesAsNumpy(),
            "snowfall": hourly.Variables(6).ValuesAsNumpy(),
            "snow_depth": hourly.Variables(7).ValuesAsNumpy(),
            "cloud_cover": hourly.Variables(8).ValuesAsNumpy(),
            "wind_speed_10m": hourly.Variables(9).ValuesAsNumpy()
        }

        self.hourly_dataframe: pd.DataFrame = pd.DataFrame(data=self.hourly_data)

    def get_current_weather(self) -> Dict[str, Any]:
        """Gibt die aktuellen Wetterdaten zurück."""
        return self.current_data

    def get_hourly_weather(self) -> pd.DataFrame:
        """Gibt die stündlichen Wetterdaten als DataFrame zurück."""
        return self.hourly_dataframe

    def get_highest_temperature(self) -> float:
        """Gibt die höchste Temperatur aus den stündlichen Daten zurück."""
        return self.hourly_dataframe["temperature_2m"].max()

    def print_current_weather(self) -> None:
        """Gibt die aktuellen Wetterdaten aus und speichert sie in einer CSV-Datei."""
        current_df = pd.DataFrame([self.current_data])
        current_df.to_csv('current_weather.csv', index=False)
        print(f"Current weather saved to 'current_weather.csv'")

    def print_hourly_weather(self) -> None:
        """Gibt die stündlichen Wetterdaten aus und speichert sie in einer CSV-Datei."""
        self.hourly_dataframe.to_csv('hourly_weather.csv', index=False)
        print(f"Hourly weather saved to 'hourly_weather.csv'")




def main():

    # Nutzung der Klasse
    latitude = 50.935173  # Köln
    longitude = 6.95310
    past_days = 0  # 92  # 3 Monate
    forecast_days = 6  # Wettervorhersage für x Tage
    weather = WeatherData(latitude, longitude, past_days, forecast_days)

    # Ausgabe und Speichern der aktuellen Wetterdaten
    weather.print_current_weather()

    # Ausgabe und Speichern der stündlichen Wetterdaten
    weather.print_hourly_weather()
#    print(weather.hourly_dataframe)
    # Ausgabe der höchsten Temperatur der stündlichen Daten
    highest_temp = weather.get_highest_temperature()
    #print(f"Highest temperature: {highest_temp} °C")

 #   print(weather.hourly_dataframe['precipitation_probability'])
    result = weather.hourly_dataframe['precipitation_probability']
    print(result.any(axis=0))

    if result.any(axis=0) == True:
         with open("output.txt", "w") as file:
            file.write("1")
    else:
        with open("output.txt", "w") as file:
            file.write("0")


if __name__=="__main__":
        main()

