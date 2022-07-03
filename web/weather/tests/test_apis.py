from unittest.mock import patch

import pytest
from django.urls import reverse

from rest_framework.test import APIClient

from web.weather.models import Weather
from web.weather.services import OpenWeatherMapClient, AlertService

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@patch.object(OpenWeatherMapClient, "weather", return_value={"main": {"temp": 10}})
def test_weather_api_persists(patch_weather, api_client):
    response = api_client.post(
        reverse("weather-create"),
        {
            "lat": 1,
            "lon": 2,
            "destination": "person@place.com",
            "alerts": {
                "min_temp": 0,
            },
        },
        format="json",
    )
    assert response.status_code == 201
    assert Weather.objects.filter(destination="person@place.com").count() == 1


@patch.object(OpenWeatherMapClient, "weather", return_value={"main": {"temp": 10}})
def test_weather_required_fields(patch_weather, api_client):
    response = api_client.post(reverse("weather-create"), format="json")
    assert response.status_code == 400
    for param in ["lat", "lon", "destination", "alerts"]:
        assert param in response.data
        assert response.data[param][0].code == "required"


@patch.object(OpenWeatherMapClient, "weather", return_value={"main": {"temp": 10}})
def test_weather_alerts_field_validation_non_empty(patch_weather, api_client):
    response = api_client.post(
        reverse("weather-create"),
        {
            "lat": 1,
            "lon": 2,
            "destination": "person@place.com",
            "alerts": {},
        },
        format="json",
    )
    assert response.status_code == 400
    assert response.data["alerts"][0].code == "empty"


@patch.object(OpenWeatherMapClient, "weather", return_value={"main": {"temp": 10}})
def test_weather_alerts_field_validation_unknown(patch_weather, api_client):
    response = api_client.post(
        reverse("weather-create"),
        {
            "lat": 1,
            "lon": 2,
            "destination": "person@place.com",
            "alerts": {"bad-alert": 1},
        },
        format="json",
    )
    assert response.status_code == 400
    assert response.data["alerts"][0].code == "unknown-alert"


@patch.object(OpenWeatherMapClient, "weather", return_value={"main": {"temp": 10}})
def test_weather_api_alert_id_returned(patch_weather, api_client):
    response = api_client.post(
        reverse("weather-create"),
        {
            "lat": 1,
            "lon": 2,
            "destination": "person@place.com",
            "alerts": {
                "min_temp": 0,
            },
        },
        format="json",
    )
    assert "id" in response.data
    assert response.data["id"] == str(
        Weather.objects.filter(destination="person@place.com").get().id
    )


@patch.object(OpenWeatherMapClient, "weather", return_value={"main": {"temp": 10}})
def test_get_previous_alert(patch_weather, api_client):
    params = {
        "lat": 1,
        "lon": 2,
        "destination": "person@place.com",
        "alerts": {
            "min_temp": 0,
        },
    }
    # Post a weather check
    response_1 = api_client.post(reverse("weather-create"), params, format="json")
    assert response_1.status_code == 201
    # Get back previously posted weather check
    response_2 = api_client.get(
        reverse("weather-retrieve", args=[response_1.data["id"]])
    )
    assert response_2.status_code == 200
    assert response_2.data["lat"] == params["lat"]
    assert response_2.data["lon"] == params["lon"]
    assert response_2.data["destination"] == params["destination"]
    assert response_2.data["alerts"] == params["alerts"]


@patch.object(OpenWeatherMapClient, "weather", return_value={"main": {"temp": 10}})
@patch.object(AlertService, "temperature_alert")
def test_api_calls_weather_client(patch_temp_alert, patch_weather, api_client):
    api_client.post(
        reverse("weather-create"),
        {
            "lat": 1,
            "lon": 2,
            "destination": "person@place.com",
            "alerts": {
                "min_temp": 0,
            },
        },
        format="json",
    )
    patch_weather.assert_called_once_with(lat=1, lon=2)


@patch.object(OpenWeatherMapClient, "weather", return_value={"main": {"temp": 10}})
@patch.object(AlertService, "send_alert")
def test_api_does_not_send_alert(patch_send_alert, patch_weather, api_client):
    api_client.post(
        reverse("weather-create"),
        {
            "lat": 1,
            "lon": 2,
            "destination": "person@place.com",
            "alerts": {
                "min_temp": 0,
            },
        },
        format="json",
    )
    patch_weather.assert_called_once_with(lat=1, lon=2)
    assert not patch_send_alert.called


@patch.object(OpenWeatherMapClient, "weather", return_value={"main": {"temp": 10}})
@patch.object(AlertService, "send_alert")
def test_api_sends_alert(patch_send_alert, patch_weather, api_client):
    api_client.post(
        reverse("weather-create"),
        {
            "lat": 1,
            "lon": 2,
            "destination": "person@place.com",
            "alerts": {
                "min_temp": 11,
            },
        },
        format="json",
    )
    assert patch_send_alert.called
