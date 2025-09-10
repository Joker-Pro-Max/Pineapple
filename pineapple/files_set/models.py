from django.conf import settings
from django.db import models
from account.models import BaseModel, User


# Create your models here.

class Category(BaseModel):

    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "Categories"


class Labels(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="标签名称")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="创建人")


class Resources(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="files", verbose_name="分类")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   verbose_name="创建人")
    resources_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="资源名称", db_index=True)
    resources_size = models.BigIntegerField(null=True, blank=True, verbose_name="资源大小")
    resources_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="资源类型")

    class Meta:
        db_table = "resources"
        verbose_name_plural = "Resources"
