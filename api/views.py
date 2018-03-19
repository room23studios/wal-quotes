import random

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import IntegrityError
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Quote, Daily
from api.serializers import QuoteSerializer
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAdminUser
from rest_framework.throttling import UserRateThrottle
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class QuoteList(APIView):
    """
    Returns all accepted quotes.
    """

    def get(self, request, format=None):
        quotes = Quote.objects.filter(accepted=True)
        serializer = QuoteSerializer(quotes, many=True)
        return Response({'status': 'success',
                         'quote': serializer.data})


@method_decorator(csrf_exempt, name='dispatch')
class QuoteDetails(APIView):
    """
    get:
    Returns quote with supplied id.
    delete:
    Deletes quote with supplied id. Requires admin token.
    """

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
        return Response({'status': 'success',
                         'quote': serializer.data,
                         'next': next_id,
                         'prev': prev_id})

    def delete(self, request, id, format=None):
        try:
            auth = JSONWebTokenAuthentication()
            user = auth.authenticate(request=request)
            if user is not None and user[0].is_superuser:
                Quote.objects.get(id=id).delete()
                return Response({'status': 'success'})
            else:
                return Response({'status': 'Error',
                                 'message': 'Authentication failed'})
        except AuthenticationFailed:
            return Response({'status': 'Error',
                             'message': 'Authentication failed'})


@method_decorator(csrf_exempt, name='dispatch')
class QuoteSubmit(APIView):
    """
    post:
    Submits supplied quote (date and annotation are optional) with accepted=False.
    Sends email to all admins containing quote and links to accept or delete quote.
    If additionally supplied with admin token, quote gets accepted automatically.
    """
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
                token = get_random_string(length=32)
                quote = serializer.save(accepted=False, token=make_password(token))

                print(request.data['text']
                      + "\nTo accept: https://alo-quotes.tk/api/accept_with_token/"
                      + str(quote.id) + "/" + token + "\n"
                      + "To reject: https://alo-quotes.tk/api/reject_with_token/"
                      + str(quote.id) + "/" + token)

                emails_pre = list(User.objects.filter(is_staff=True).all().values_list('email'))
                emails = [email[0] for email in emails_pre]
                send_mail(
                    'New quote submitted',
                    request.data['text']
                    + "\nTo accept: https://alo-quotes.tk/api/accept_with_token/"
                    + str(quote.id) + "/" + token + "\n"
                    + "To reject: https://alo-quotes.tk/api/reject_with_token/"
                    + str(quote.id) + "/" + token,
                    'submission-bot@alo-quotes.tk',
                    emails,
                    fail_silently=False, )

            return Response({'status': 'success',
                             'quote': serializer.data})
        return Response({'status': 'Error',
                         'messages': serializer.errors})


class QuoteRandom(APIView):
    """
    get:
    Returns a random quote.
    """

    def get(self, request, format=None):
        count = Quote.objects.filter(accepted=True).count()
        quote = Quote.objects.filter(accepted=True)[int(random.random() * count)]
        serializer = QuoteSerializer(quote)
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
        return Response({'status': 'success',
                         'quote': serializer.data,
                         'next': next_id,
                         'prev': prev_id})


@method_decorator(csrf_exempt, name='dispatch')
class QuoteAccept(APIView):
    """
    post:
    Accepts a quote with supplied id. Requires admin token.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdminUser,)

    def post(self, request, id, format=None):
        quote = Quote.objects.get(id=id)
        quote.accepted = True
        quote.save()
        return Response({'status': 'success'})


class QuoteAcceptToken(APIView):
    """
    get:
    Accepts quote with supplied id.
    Requires token assigned to that quote.
    Used in email messaging.
    """

    def get(self, request, id, token, format=None):
        try:
            quote = Quote.objects.get(id=id)
            if check_password(token, quote.token):
                quote.accepted = True
                quote.save()
                return Response({'status': 'success'})
            else:
                return Response({'status': 'Error',
                                 'message': 'Token does not match'})
        except Quote.DoesNotExist:
            return Response({'status': 'Error',
                             'message': 'Quote with this id does not exist'})


class QuoteRejectToken(APIView):
    """
    get:
    Deletes quote with supplied id.
    Requires token assigned to that quote.
    Used in email messaging.
    """

    def get(self, request, id, token, format=None):
        try:
            quote = Quote.objects.get(id=id)
            if check_password(token, quote.token):
                quote.delete()
                return Response({'status': 'success'})
            else:
                return Response({'status': 'Error',
                                 'message': 'Token does not match'})
        except Quote.DoesNotExist:
            return Response({'status': 'Error',
                             'message': 'Quote with this id does not exist'})


class QuoteSubmissions(APIView):
    """
    get:
    Returns a list of not yet accepted quotes.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdminUser,)

    def get(self, request, format=None):
        quotes = Quote.objects.filter(accepted=False)
        serializer = QuoteSerializer(quotes, many=True)
        return Response({'status': 'success',
                         'quote': serializer.data})


@method_decorator(csrf_exempt, name='dispatch')
class DailyDetails(APIView):
    """
    get:
    Returns a daily quote.
    post:
    Selects a new daily quote.
    """

    def get(self, request, format=None):
        try:
            quote_id = Daily.objects.latest('date').quote_id
            print(quote_id)
            serializer = QuoteSerializer(Quote.objects.get(id=quote_id))
            return Response({'status': 'success',
                             'quote': serializer.data})
        except Daily.DoesNotExist:
            return Response({'status': 'Error',
                             'message': 'Daily does not exists'})

    def post(self, request, format=None):
        try:
            auth = JSONWebTokenAuthentication()
            user = auth.authenticate(request=request)
            if user is not None and user[0].is_superuser:
                count = Quote.objects.filter(accepted=True).count()
                quote_id = Quote.objects.filter(accepted=True)[int(random.random() * count)].id
                try:
                    while quote_id == Daily.objects.latest('date').quote_id:
                        quote_id = Quote.objects.filter(accepted=True)[int(random.random() * count)].id
                except Daily.DoesNotExist:
                    pass
                daily = Daily.objects.create(quote_id=quote_id)
                daily.save()
                return Response({'status': 'success'})
            else:
                return Response({'status': 'Error',
                                 'message': 'Authentication failed'})
        except AuthenticationFailed:
            return Response({'status': 'Error',
                             'message': 'Authentication failed'})
