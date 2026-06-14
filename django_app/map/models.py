from django.db import models

class Place(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    geocoded = models.BooleanField(default=False)
    mainlevee = models.BooleanField(default=False)
    arrondissement = models.CharField(max_length=10, blank=True, default="")

    def __str__(self):
        return self.address