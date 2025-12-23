from rest_framework import serializers
from .models import Course, File

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'name', 'file_url']

class CourseSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'files', 'created_at', 'user']