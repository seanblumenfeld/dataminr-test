from django.conf import settings
from rest_framework.generics import CreateAPIView, RetrieveAPIView

from web.weather.models import Weather
from web.weather.serializers import WeatherSerializer
from web.weather.services import OpenWeatherMapClient, AlertService


class WeatherCreateAPIView(CreateAPIView):
    serializer_class = WeatherSerializer

    def perform_create(self, serializer: WeatherSerializer) -> None:
        super().perform_create(serializer)
        client = OpenWeatherMapClient(api_key=settings.OPEN_WEATHER_MAP_API_KEY)
        weather_data = client.weather(
            lat=serializer.data["lat"], lon=serializer.data["lon"]
        )
        AlertService().temperature_alert(
            temperature=weather_data["main"]["temp"],
            alerts=serializer.data["alerts"],
            destination=serializer.data["destination"],
        )


class WeatherRetrieveAPIView(RetrieveAPIView):
    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer
