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
    # 打开生成层别名称的入口开关。之前有过这样，对于已有层别信息的料，隐藏生成层别信息的的入口，防止新生成的把原来的老信息都边覆盖了。
    # path('get_file_name_from_org_on/<int:job_id>/', views.get_file_name_from_org_on, name='get_file_name_from_org_on'),



]

