from django.conf.urls import patterns, url

from abashin_api_app import views

urlpatterns = patterns('',
    url( r'^clear$', views.clear_db),
    url( r'^(?P<entity>\S+)/(?P<method>\S+)$', views.response_page)
)