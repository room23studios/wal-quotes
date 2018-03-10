from django.conf.urls import url
from api import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from django.views.decorators.csrf import ensure_csrf_cookie

urlpatterns = [
    url(r'^quotes/$', views.QuoteList.as_view()),
    url(r'^quotes/(?P<id>[0-9]+)/$', views.QuoteDetails.as_view()),
    url(r'^submit/$', ensure_csrf_cookie(views.QuoteSubmit.as_view())),
    url(r'^random/$', views.QuoteRandom.as_view()),
    url(r'^accept/(?P<id>[0-9]+)/$', ensure_csrf_cookie(views.QuoteAccept.as_view())),
    url(r'^submissions/$', views.QuoteSubmissions.as_view()),
    url(r'^daily/$', ensure_csrf_cookie(views.DailyDetails.as_view())),
    url(r'^token_auth/$', ensure_csrf_cookie(obtain_jwt_token)),
    url(r'^token_refresh/', ensure_csrf_cookie(refresh_jwt_token)),
]

urlpatterns = format_suffix_patterns(urlpatterns)