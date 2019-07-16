from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^signals/norm/(?P<signal_id>\d+)/$', views.norm, name='norm'),
    url(r'^signals/zscore/(?P<signal_id>\d+)/$', views.zscore, name='zscore'),
    url(r'^signals/combine/$', views.combine, name='combine')
]
