import csv
import json
from unittest.mock import create_autospec
from urllib.parse import urljoin

import pytest
import requests
import requests_mock

from web.weather.services import OpenWeatherMapClient, AlertService


@pytest.fixture
def data():
    return {}


@pytest.fixture
def adapter(data):
    _adapter = requests_mock.Adapter()
    _adapter.register_uri(
        method="GET",
        url=urljoin(OpenWeatherMapClient.base_url, "weather/"),
        text=json.dumps(data),
        complete_qs=False,
    )
    return _adapter


@pytest.fixture
def session(adapter):
    _session = requests.Session()
    _session.mount("https://", adapter)
    return _session


@pytest.fixture
def open_weather_map_client(session):
    return OpenWeatherMapClient(api_key="fake", session=session)


@pytest.fixture
def destination():
    return "person@place.com"


@pytest.fixture
def alerts():
    return {"min_temp": 0}


@pytest.fixture
def csv_adapter():
    return create_autospec(csv)


@pytest.fixture
def alert_service(csv_adapter):
    return AlertService(csv_adapter=csv_adapter)


def test_weather_query_contains_lat_long(adapter, open_weather_map_client):
    open_weather_map_client.weather(lat=1, lon=2)
    assert "lat=1&lon=2" in adapter.last_request.query


def test_weather_query_contains_api_key(adapter, open_weather_map_client):
    open_weather_map_client.weather(lat=1, lon=2)
    assert "appid=fake" in adapter.last_request.query


def test_weather_raise_for_status(adapter, open_weather_map_client):
    adapter.register_uri(  # TODO: setting up uri responses can be tidied up with more time
        method="GET",
        url=urljoin(OpenWeatherMapClient.base_url, "weather/"),
        exc=requests.exceptions.HTTPError,
        complete_qs=False,
    )
    with pytest.raises(requests.exceptions.HTTPError):
        open_weather_map_client.weather(lat=1, lon=2)


def test_weather_result(data, open_weather_map_client):
    result = open_weather_map_client.weather(lat=1, lon=2)
    assert result == data


def test_alert_service_does_not_send_alert(
    alert_service, alerts, destination, csv_adapter
):
    alert_service.temperature_alert(
        temperature=5, alerts=alerts, destination=destination
    )
    assert not csv_adapter.writer.called


def test_alert_service_sends_alert(alert_service, csv_adapter, destination, alerts):
    alert_service.temperature_alert(
        temperature=-5, alerts=alerts, destination=destination
    )
    csv_adapter.writer.return_value.writerow.assert_called_once_with(
        [-5, alerts, destination]
    )
