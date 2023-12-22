# backend/serializers.py

from rest_framework import serializers
from .models import JobForTest
from django.contrib.auth.models import User  # 导入User模型

class JobForTestSerializer(serializers.ModelSerializer):
    # author = serializers.StringRelatedField(source='author.username')  # 指定author字段的显示方式
    author = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())  # 指定author字段的显示方式
    test_usage_for_epcam_module = serializers.StringRelatedField(source='test_usage_for_epcam_module.name',
                                                                 read_only=True)
    class Meta:
        model = JobForTest
        fields = '__all__'
