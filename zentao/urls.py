from django.contrib.auth.decorators import login_required
from django.urls import path, re_path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings
app_name = 'zentao'
urlpatterns = [
    path('BugView', views.BugView.as_view(),name='BugView'),#类视图，删除料号。

    path('TestView', views.TestView.as_view(), name='TestView'),
    path('TestJsonView',views.TestJsonView.as_view(),name='TestJsonView')



]

