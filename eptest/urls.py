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

    path('JobForTestDetailViewForm/<int:pk>', views.JobForTestDetailViewForm.as_view(), name='JobForTestDetailViewForm'),#点击标签调用的。

    path('JobForTestUpdateView/<int:pk>/<int:current_page>', views.JobForTestUpdateView.as_view(), name='JobForTestUpdateView'),#类视图，用来更新料号的。

    path('JobForTestCreateView', views.JobForTestCreateView.as_view(), name='JobForTestCreateView'),#类视图，新增料号。

    path('JobForTestDeleteView/<int:pk>', views.JobForTestDeleteView.as_view(),name='JobForTestDeleteView'),#类视图，删除料号。


    # 根据整理过的gerber压缩包，生成层别信息。
    path('get_layer_name_from_org/<int:job_id>/', views.get_layer_name_from_org, name='get_layer_name_from_org'),


    path('send_vs_g_local_result', views.send_vs_g_local_result,name='send_vs_g_local_result'),#开发时测试用的。



]

