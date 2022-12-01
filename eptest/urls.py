from django.contrib.auth.decorators import login_required
from django.urls import path,re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
app_name = 'eptest'
urlpatterns = [

    path('epcam_module/', views.show_genres),

    path('JobForTestListView',login_required(views.JobForTestListView.as_view()),name='JobForTestListView'),#类视图，用来组普通用户展示料号列表的。

    path('tag/<str:tag_slug>/',  views.JobForTestListView.as_view(), name='job_list_by_tag'), # 这里的参数类型不要写slug，否则又会忽视中文，写str就行了
    #
    # path('JobDetailView/<int:pk>', views.JobDetailView.as_view(), name='JobDetailView'),#类视图。
    # path('JobDetailViewForm/<int:pk>', views.JobDetailViewForm.as_view(), name='JobDetailViewForm'),#点击标签调用的。
    #
    # path('JobUpdateView/<int:pk>/<int:current_page>', views.JobUpdateView.as_view(), name='JobUpdateView'),#类视图，用来更新料号的。
    #
    # path('JobCreateView', views.JobCreateView.as_view(), name='JobCreateView'),#类视图，新增料号。
    #
    # path('JobDeleteView/<int:pk>', views.JobDeleteView.as_view(),name='JobDeleteView'),#类视图，删除料号。




]

