from django.contrib.auth.decorators import login_required
from django.urls import path,re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
app_name = 'job'
urlpatterns = [

    path('JobListView',login_required(views.JobListView.as_view()),name='JobListView'),#类视图，用来组普通用户展示料号列表的。

    path('tag/<str:tag_slug>/',  views.JobListView.as_view(), name='job_list_by_tag'), # 这里的参数类型不要写slug，否则又会忽视中文，写str就行了

    path('JobDetailView/<int:pk>', views.JobDetailView.as_view(), name='JobDetailView'),#类视图。
    path('JobDetailViewForm/<int:pk>', views.JobDetailViewForm.as_view(), name='JobDetailViewForm'),#类视图。


]

