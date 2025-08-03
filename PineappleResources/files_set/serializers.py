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


# ✅ 文件元数据序列化器
class FileMetaSerializer(serializers.ModelSerializer):
    category_info = CategorySerializer(source="category", read_only=True)
    # 🔹 关联分类详情
    created_info = UserBriefSerializer(source="created_by", read_only=True)

    # 🔹 关联上传者详情

    class Meta:
        model = FileMeta
        fields = [
            "uuid",  # 文件 UUID
            "filename",  # 文件名
            "content_type",  # MIME 类型
            "file_size",  # 文件大小
            "mongo_id",  # MongoDB GridFS ID
            "category",  # 分类 UUID（用于提交）
            "category_info",  # 分类详情（用于展示）
            "created_by",  # 上传用户 ID（提交用）
            "created_info",  # 上传用户详情（展示用）
            "create_at",  # 上传时间
        ]
        read_only_fields = ["uuid", "mongo_id", "created_by", "create_at"]
