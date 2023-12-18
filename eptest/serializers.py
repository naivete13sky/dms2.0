# backend/serializers.py

from rest_framework import serializers
from .models import JobForTest

class JobForTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobForTest
        fields = '__all__'
