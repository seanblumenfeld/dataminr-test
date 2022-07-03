from rest_framework import serializers

from web.weather.models import Weather
from web.weather.services import AlertService


class WeatherSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Weather
        fields = ["id", "lat", "lon", "destination", "alerts"]
        read_only_fields = ["id"]

    def validate_alerts(self, value):
        if not value:
            raise serializers.ValidationError("Empty", "empty")
        if not set(value.keys()).issubset(set(AlertService.alert_definitions.keys())):
            raise serializers.ValidationError("Unknown alert", "unknown-alert")
        return value
