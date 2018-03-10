import random

from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Quote, Daily
from api.serializers import QuoteSerializer
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAdminUser
from rest_framework.throttling import UserRateThrottle


class QuoteList(APIView):
    def get(self, request, format=None):
        quotes = Quote.objects.filter(accepted=True)
        serializer = QuoteSerializer(quotes, many=True)
        return Response(serializer.data)


class QuoteDetails(APIView):
    def get(self, request, id, format=None):
        user = None
        try:
            try:
                auth = JSONWebTokenAuthentication()
                user = auth.authenticate(request=request)
            except AuthenticationFailed:
                pass

            if user is not None and user[0].is_superuser:
                quote = Quote.objects.get(id=id)
            else:
                quote = Quote.objects.filter(accepted=True).get(id=id)

            prev_quote = Quote.objects.filter(id__lte=quote.id, accepted=True).exclude(id=quote.id).order_by(
                '-id').first()
            next_quote = Quote.objects.filter(id__gte=quote.id, accepted=True).exclude(id=quote.id).order_by(
                'id').first()
            if prev_quote is not None:
                prev_id = prev_quote.id
            else:
                prev_id = None
            if next_quote is not None:
                next_id = next_quote.id
            else:
                next_id = None

        except Quote.DoesNotExist:
            return Response({'status': 'Error',
                             'message': 'Quote does not exists'})
        serializer = QuoteSerializer(quote)
        return Response({'status': 'Success',
                         'quote': serializer.data,
                         'next': next_id,
                         'prev': prev_id})

    def delete(self, request, id, format=None):
        try:
            auth = JSONWebTokenAuthentication()
            user = auth.authenticate(request=request)
            if user is not None and user[0].is_superuser:
                Quote.objects.get(id=id).delete()
                return Response({'status': 'Success'})
            else:
                return Response({'status': 'Error',
                                 'message': 'Authentication failed'})
        except AuthenticationFailed:
            return Response({'status': 'Error',
                             'message': 'Authentication failed'})


class QuoteSubmit(APIView):
    throttle_classes = (UserRateThrottle,)



    def post(self, request):
        serializer = QuoteSerializer(data=request.data)
        if serializer.is_valid():
            user = None
            try:
                auth = JSONWebTokenAuthentication()
                user = auth.authenticate(request=request)
            except AuthenticationFailed:
                pass
            if user is not None and user[0].is_superuser:
                serializer.save(accepted=True)
            else:
                serializer.save(accepted=False)
            return Response({'status': 'Success',
                             'quote': serializer.data})
        return Response({'status': 'Error',
                         'messages': serializer.errors})


class QuoteRandom(APIView):
    def get(self, request, format=None):
        count = Quote.objects.all().count()
        quote = Quote.objects.all()[int(random.random() * count)]
        serializer = QuoteSerializer(quote)
        return Response({'status': 'Success',
                         'quote': serializer.data})


class QuoteAccept(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdminUser,)

    def post(self, request, id, format=None):
        quote = Quote.objects.get(id=id)
        quote.accepted = True
        quote.save()
        return Response({'status': 'Success'})


class QuoteSubmissions(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdminUser,)

    def get(self, request, format=None):
        quotes = Quote.objects.filter(accepted=False)
        serializer = QuoteSerializer(quotes, many=True)
        return Response({'status': 'Success',
                         'quote': serializer.data})


class DailyDetails(APIView):

    def get(self, request, format=None):
        try:
            quote_id = Daily.objects.latest('date').quote_id
            print(quote_id)
            serializer = QuoteSerializer(Quote.objects.get(id=quote_id))
            return Response({'status': 'Success',
                             'quote': serializer.data})

        except Daily.DoesNotExist:
            return Response({'status': 'Error',
                             'message': 'Daily does not exists'})

    def post(self, request, format=None):
        try:
            auth = JSONWebTokenAuthentication()
            user = auth.authenticate(request=request)
            if user is not None and user[0].is_superuser:
                count = Quote.objects.all().count()
                daily = Daily.objects.create(quote_id=Quote.objects.all()[int(random.random() * count)].id)
                daily.save()
                return Response({'status': 'Success'})
            else:
                return Response({'status': 'Error',
                                 'message': 'Authentication failed'})
        except AuthenticationFailed:
            return Response({'status': 'Error',
                             'message': 'Authentication failed'})
