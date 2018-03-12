from django.core.management.base import BaseCommand, CommandError
from api.models import Daily
from api.models import Quote
import random

class Command(BaseCommand):
    help = 'Makes new daily quote'

    def handle(self, *args, **options):
        count = Quote.objects.filter(accepted=True).count()
        quote_id = Quote.objects.filter(accepted=True)[int(random.random() * count)].id
        try:
            if count > 1:
                while quote_id == Daily.objects.latest('date').quote_id:
                    quote_id = Quote.objects.filter(accepted=True)[int(random.random() * count)].id
        except Daily.DoesNotExist:
            pass
        daily = Daily.objects.create(quote_id=quote_id)
        daily.save()

        self.stdout.write(self.style.SUCCESS('Successfully created new daily of id "%s"' % quote_id))