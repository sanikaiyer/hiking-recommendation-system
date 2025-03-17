from django.db import models

class Trail(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=50)
    distance = models.FloatField()  # In miles
    elevation = models.FloatField()  # In feet
    rating = models.FloatField()  # Out of 5

    def __str__(self):
        return self.name

