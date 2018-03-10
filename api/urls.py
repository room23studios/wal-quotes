from django.conf.urls import url
from api import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [
    url(r'^quotes/$', views.QuoteList.as_view()),
    url(r'^quotes/(?P<id>[0-9]+)/$', views.QuoteDetails.as_view()),
    url(r'^submit/$', views.QuoteSubmit.as_view()),
    url(r'^random/$', views.QuoteRandom.as_view()),
    url(r'^accept/(?P<id>[0-9]+)/$', views.QuoteAccept.as_view()),
    url(r'^submissions/$', views.QuoteSubmissions.as_view()),
    url(r'^daily/$', views.DailyDetails.as_view()),
    url(r'^token_auth/$', obtain_jwt_token),
    url(r'^token_refresh/', refresh_jwt_token),
]

urlpatterns = format_suffix_patterns(urlpatterns)