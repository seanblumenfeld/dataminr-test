import csv
import operator
from urllib.parse import urljoin
from typing import Optional, Any

import requests


class OpenWeatherMapClient:
    base_url = "https://api.openweathermap.org/data/2.5/"

    def __init__(
        self, api_key: str, session: Optional[requests.Session] = None
    ) -> None:
        self.session = session or requests.Session()
        self.api_key = api_key

    def weather(self, lat: int, lon: int) -> dict:
        response = self.session.get(
            url=urljoin(self.base_url, "weather/"),
            params={
                "lat": lat,
                "lon": lon,
                "units": "metric",
                "appid": self.api_key,
            },
        )
        response.raise_for_status()
        return response.json()


class AlertService:
    alert_definitions = {
        "min_temp": {
            "name": "min_temp",
            "operator": operator.lt,
        },
        "max_temp": {
            "name": "max_temp",
            "operator": operator.gt,
        },
    }

    def __init__(self, csv_adapter: Any = None) -> None:
        self.alerts_filename = "alerts.csv"
        self.csv_adapter = csv_adapter or csv

    def send_alert(self, temperature: float, alerts: dict, destination: str) -> None:
        with open(self.alerts_filename, "w") as csvfile:
            writer = self.csv_adapter.writer(csvfile)
            writer.writerow([temperature, alerts, destination])

    def temperature_alert(
        self, temperature: float, alerts: dict, destination: str
    ) -> None:
        for alert_name, alert_value in alerts.items():
            alert_definition = self.alert_definitions[alert_name]
            if alert_definition["operator"](temperature, alert_value):
                self.send_alert(
                    temperature=temperature, alerts=alerts, destination=destination
                )
