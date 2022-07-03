from uuid import uuid4

from django.db import models


class Weather(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    lat = models.IntegerField()
    lon = models.IntegerField()
    destination = models.CharField(
        max_length=100
    )  # TODO: could put some validation on this field
    alerts = models.JSONField()  # TODO: this could be in another model
