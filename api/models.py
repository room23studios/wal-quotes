from django.db import models
from rest_framework.authtoken.models import Token


class Quote(models.Model):
    text = models.TextField(unique=True)
    date = models.DateTimeField(blank=True, null=True)
    annotation = models.TextField(blank=True, null=True)
    accepted = models.BooleanField(default=False)


class Daily(models.Model):
    quote_id = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)