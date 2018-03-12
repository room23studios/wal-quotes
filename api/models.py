from django.db import models
from rest_framework.authtoken.models import Token


class Quote(models.Model):
    text = models.TextField(unique=True)
    date = models.DateField(blank=True, null=True)
    annotation = models.TextField(blank=True, null=True)
    accepted = models.BooleanField(default=False)
    token = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.text


class Daily(models.Model):
    quote_id = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return Quote.objects.get(id=self.quote_id)