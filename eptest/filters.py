# filters.py
import django_filters
from .models import JobForTest
from django.db import models
from taggit.managers import TaggableManager
from django_filters import ModelMultipleChoiceFilter
from django_filters import ModelChoiceFilter

class JobForTestFilter(django_filters.FilterSet):
    class Meta:
        model = JobForTest
        # fields = '__all__'
        fields = ['tags','file_type','status','author','test_usage_for_epcam_module']
        # fields = ['file_type','status','tags__name']

        filter_overrides = {
            models.FileField: {
                'filter_class': django_filters.CharFilter,  # 使用 CharFilter 作为过滤器类
                'extra': lambda f: {'lookup_expr': 'icontains'},  # 这里可以根据需要设置其他参数
            },
            # TaggableManager: {
            #     'filter_class': django_filters.CharFilter,  # 使用 CharFilter 作为过滤器类
            #     # 'extra': lambda f: {'lookup_expr': 'icontains'},  # 这里可以根据需要设置其他参数
            #     'extra': lambda f: {'lookup_expr': 'in'},  # 使用 'in' 查找表达式
            # },
            # TaggableManager: {
            #     'filter_class': ModelMultipleChoiceFilter,  # 使用 ModelMultipleChoiceFilter
            #     'extra': lambda f: {'queryset': f.model.tags.all()},  # 通过 tags.all() 获取合适的 queryset
            # },
            TaggableManager: {
                'filter_class': ModelChoiceFilter,  # 使用 ModelChoiceFilter
                'extra': lambda f: {'queryset': f.model.tags.all()},  # 通过 tags.all() 获取合适的 queryset
            },
        }