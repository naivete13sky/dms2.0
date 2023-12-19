# filters.py
import django_filters
from .models import JobForTest
from django.db import models
from taggit.managers import TaggableManager

class JobForTestFilter(django_filters.FilterSet):
    class Meta:
        model = JobForTest
        fields = '__all__'
        filter_overrides = {
            models.FileField: {
                'filter_class': django_filters.CharFilter,  # 使用 CharFilter 作为过滤器类
                'extra': lambda f: {'lookup_expr': 'icontains'},  # 这里可以根据需要设置其他参数
            },
            TaggableManager: {
                'filter_class': django_filters.CharFilter,  # 使用 CharFilter 作为过滤器类
                'extra': lambda f: {'lookup_expr': 'icontains'},  # 这里可以根据需要设置其他参数
            },
        }