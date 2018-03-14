from django.conf.urls import url
from api import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework_swagger.views import get_swagger_view

urlpatterns = [
    url(r'^quotes/$', views.QuoteList.as_view()),
    url(r'^quotes/(?P<id>[0-9]+)/$', ensure_csrf_cookie(views.QuoteDetails.as_view())),
    url(r'^submit/$', ensure_csrf_cookie(views.QuoteSubmit.as_view())),
    url(r'^random/$', views.QuoteRandom.as_view()),
    url(r'^accept/(?P<id>[0-9]+)/$', ensure_csrf_cookie(views.QuoteAccept.as_view())),
    url(r'^submissions/$', views.QuoteSubmissions.as_view()),
    url(r'^daily/$', ensure_csrf_cookie(views.DailyDetails.as_view())),
    url(r'^token_auth/$', ensure_csrf_cookie(obtain_jwt_token)),
    url(r'^token_refresh/', ensure_csrf_cookie(refresh_jwt_token)),
    url(r'^accept_with_token/(?P<id>[0-9]+)/(?P<token>.*)/$', views.QuoteAcceptToken.as_view()),
    url(r'^reject_with_token/(?P<id>[0-9]+)/(?P<token>.*)/$', views.QuoteRejectToken.as_view()),
    url(r'^docs', get_swagger_view(title='Alo Quotes API'))
]

urlpatterns = format_suffix_patterns(urlpatterns)