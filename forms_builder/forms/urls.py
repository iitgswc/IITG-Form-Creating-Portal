from __future__ import unicode_literals

from django.conf.urls import url

from forms_builder.forms import views

app_name='forms'

urlpatterns = [
    url(r'^$', views.MainView.as_view(), name='main'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(r'^(?P<formid>.*)/exportcsv/$', views.ExportCsvView.as_view(), name='exportcsv'),
    url(r'^createfield/$', views.CreateFieldView.as_view(), name='createfield'),
    url(r'^test/$', views.TestView.as_view(), name='test'),
    url(r'(?P<slug>.*)/sent/$', views.form_sent, name="form_sent"),
    url(r'(?P<slug>.*)/$', views.form_detail, name="form_detail"),
]
