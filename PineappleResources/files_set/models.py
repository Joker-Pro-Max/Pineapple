from django.conf import settings
from django.db import models

from account.models import BaseModel, User


# Create your models here.

class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class FileMeta(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="files")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    filename = models.CharField(max_length=255)  # 上传时的文件名
    content_type = models.CharField(max_length=100)
    file_size = models.BigIntegerField()
    file_path = models.CharField(max_length=500, default="")  # 实际文件存储路径
    file_hash = models.CharField(max_length=64, default="")  # 文件去重依据（SHA256）
