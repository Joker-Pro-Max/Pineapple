import shortuuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


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


# ✅ 2. 业务系统表 System
class System(BaseModel):
    """
    业务系统表（标识各个微服务）
    """
    system_name = models.CharField(max_length=100, verbose_name="系统名称", db_index=True)
    system_code = models.CharField(max_length=50, unique=True, verbose_name="系统唯一标识", db_index=True)  # 系统唯一标识
    # 系统描述

    # ✅ 新增创建人
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="created_systems",
        verbose_name="创建人"
    )

    def __str__(self):
        return f"{self.system_name} ({self.system_code})"


# ✅ 3. 自定义权限表 CustomPermission
class CustomPermission(BaseModel):
    """
    自定义权限（独立于 Django 默认权限）
    """
    permission_name = models.CharField(max_length=100, verbose_name="权限名称", db_index=True)
    permission_code = models.CharField(max_length=100, unique=True, verbose_name="权限code",
                                       db_index=True)  # 例如: product.view
    # ✅ 新增创建人
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="created_custom_permissions",
        verbose_name="创建人"
    )

    def __str__(self):
        return f"{self.permission_name} ({self.permission_code})"


# ✅ 4. 角色表 Role
class Role(BaseModel):
    """
    角色表（可分配给用户，并关联自定义权限）
    """
    role_name = models.CharField(max_length=100, unique=True, verbose_name="角色名称", db_index=True)
    is_enable = models.BooleanField(default=True, verbose_name="是否启用", db_index=True)

    # 角色描述

    # 🔗 角色 ↔ 权限
    permissions = models.ManyToManyField(
        CustomPermission,
        related_name="roles",
        blank=True,
        verbose_name="权限"
    )
    # ✅ 新增创建人
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="created_roles",
        verbose_name="创建人"
    )

    def __str__(self):
        return self.role_name


# ✅ 5. 用户管理器
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


# ✅ 6. 用户表 User
class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    用户表（统一账户中心）
    """
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="email", db_index=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="phone", db_index=True)
    password = models.CharField(max_length=128, null=True, blank=True, verbose_name="password")
    avatar = models.URLField(null=True, blank=True, verbose_name="avatar", db_index=True)
    username = models.CharField(max_length=150, null=True, blank=True, verbose_name="username", db_index=True)
    nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name="nickname", db_index=True)

    # ✅ 微信字段
    wx_openid = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name="wx_openid",
                                 db_index=True)
    wx_unionid = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name="wx_unionid",
                                  db_index=True)
    wx_nickname = models.CharField(max_length=100, null=True, blank=True, verbose_name="wx_nickname", db_index=True)
    wx_avatar_url = models.URLField(null=True, blank=True, verbose_name="wx_avatar_url", db_index=True)

    # ✅ Django 内置权限字段
    is_active = models.BooleanField(default=True, verbose_name="is_active", db_index=True)
    is_staff = models.BooleanField(default=False, verbose_name="is_staff", db_index=True)

    # 🔗 用户 ↔ 角色（多对多）
    roles = models.ManyToManyField(
        Role,
        related_name="users",
        blank=True,
        verbose_name="roles",
    )

    # 🔗 用户 ↔ 系统（用户可以注册到多个业务系统）
    systems = models.ManyToManyField(
        System,
        related_name="users",
        blank=True,
        verbose_name="systems",
    )

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="account_users",  # ✅ 这里改了 related_name
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="account_user_permissions",  # ✅ 这里也改了
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(fields=["unified_uuid"], name="idx_user_unified_uuid"),
            models.Index(fields=["is_deleted", "username"], name="idx_user_deleted_username"),
            models.Index(fields=["is_deleted", "nickname"], name="idx_user_deleted_nickname"),
            models.Index(fields=["is_deleted", "email"], name="idx_user_deleted_email"),
            models.Index(fields=["is_deleted", "phone"], name="idx_user_deleted_phone"),
            models.Index(fields=["is_deleted", "email", "nickname", "wx_nickname", "username"],
                         name="idx_user_list"),
        ]

    def __str__(self):
        return self.email or f"wx_{self.wx_openid or self.unified_uuid}"

    @property
    def all_roles(self):
        """返回角色编码列表"""
        return list(self.roles.values_list("role_name", flat=True))

    @property
    def all_permissions(self):
        """
        获取所有权限（自定义权限 + Django 内置权限）
        """
        perms = set(self.get_all_permissions())  # Django 自带权限
        for role in self.roles.prefetch_related("permissions").all():
            perms.update(role.permissions.values_list("permission_code", flat=True))
        return list(perms)

    def is_super_admin(self):
        """超级管理员：Django is_superuser OR 角色 superadmin"""
        if self.is_superuser:  # ✅ 兼容 Django createsuperuser
            return True
        return self.roles.filter(role_name="superadmin", is_enable=True).exists()

    def has_custom_permission(self, perm_code):
        """
        检查用户是否拥有某个自定义权限
        """
        if self.is_super_admin():
            return True
        return self.roles.filter(
            is_enable=True,
            permissions__permission_code=perm_code
        ).exists()
