from django.contrib.auth.decorators import login_required
from django.urls import path,re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
app_name = 'job'
urlpatterns = [

    path('JobListView',login_required(views.JobListView.as_view()),name='JobListView'),#类视图，用来组普通用户展示料号列表的。

    path('tag/<str:tag_slug>/', views.job_list, name='job_list_by_tag'),


]

