import shortuuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# Create your models here.


def create_uuid():
    return shortuuid.uuid()


# ✅ 1. 基类 BaseModel
class BaseModel(models.Model):
    unified_uuid = models.CharField(
        "全系统唯一标识",
        default=create_uuid,
        unique=True,
        editable=False,
        db_index=True,
        max_length=25
    )
    uuid = models.CharField(
        "当前系统唯一标识",
        primary_key=True,
        default=create_uuid,
        editable=False,
        max_length=25,
        db_index=True
    )
    create_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    update_at = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除: True 已经删除 False 未删除", db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="删除时间")

    class Meta:
        abstract = True

    def soft_delete(self):
        """软删除"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])


class UserManager(BaseUserManager):
    def create_user(self, email=None, password=None, **extra_fields):
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)  # ✅ 这里确保密码被哈希化
        else:
            # ✅ 如果没有提供密码，生成随机密码（用于第三方登录）
            from django.utils.crypto import get_random_string
            user.set_password(get_random_string(12))
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="email", db_index=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="phone", db_index=True)
    password = models.CharField(max_length=128, null=True, blank=True, verbose_name="password")
    avatar = models.URLField(null=True, blank=True, verbose_name="avatar", db_index=True)
    username = models.CharField(max_length=150, null=True, blank=True, verbose_name="username", db_index=True)
    nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name="nickname", db_index=True)
    # ✅ Django 内置权限字段
    is_active = models.BooleanField(default=True, verbose_name="is_active", db_index=True)
    is_staff = models.BooleanField(default=False, verbose_name="is_staff", db_index=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
