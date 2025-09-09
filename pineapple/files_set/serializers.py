from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import FileMeta, Category

User = get_user_model()


# ✅ 用户简要信息
class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["uuid", "username", "nickname", "email"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["uuid", "name", "created_by", "create_at"]




class FileMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileMeta
        fields = '__all__'
        read_only_fields = ('file_path', 'file_hash', 'file_size', 'content_type', 'created_by')
