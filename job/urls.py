from django.contrib.auth.decorators import login_required
from django.urls import path,re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
app_name = 'job'
urlpatterns = [

    path('JobListView',login_required(views.JobListView.as_view()),name='JobListView'),#类视图，用来组普通用户展示料号列表的。












# ]
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
