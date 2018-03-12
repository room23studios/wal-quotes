from rest_framework import serializers
from api.models import Quote, Daily


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = ('id', 'text', 'date', 'annotation', 'accepted')