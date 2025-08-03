from django.db import models

from account.models import BaseModel, User


# Create your models here.

class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class FileMeta(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="files")
    # 🔹 文件所属分类（外键关联 Category），分类删除时文件元数据也删除

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # 🔹 上传文件的用户（外键指向 User），删除用户时置空

    filename = models.CharField(max_length=255)
    # 🔹 原始文件名（用户上传时的名称，供前端显示）

    content_type = models.CharField(max_length=100)
    # 🔹 文件 MIME 类型（如 image/png, video/mp4, application/pdf 等）

    file_size = models.BigIntegerField()
    # 🔹 文件大小（单位：字节）

    mongo_id = models.CharField(max_length=64, unique=True)
    # 🔹 MongoDB GridFS 中存储的文件 ID（关联 MongoDB 文档）
