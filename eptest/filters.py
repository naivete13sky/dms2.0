# filters.py
import django_filters
from .models import JobForTest, EpcamModule
from django.db import models
from taggit.managers import TaggableManager
from django_filters import ModelMultipleChoiceFilter
from django_filters import ModelChoiceFilter
from django.contrib.auth.models import User  # 导入User模型

class JobForTestFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name='author__username', lookup_expr='icontains')  # 使用icontains过滤username
    # test_usage_for_epcam_module = django_filters.CharFilter(field_name='test_usage_for_epcam_module__name',
    #                                                         lookup_expr='icontains')
    test_usage_for_epcam_module = ModelChoiceFilter(
        field_name='test_usage_for_epcam_module',
        queryset=EpcamModule.objects.all(),
        to_field_name='name',  # 使用名称而不是ID显示
    )
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