from rest_framework import permissions
from rest_framework.permissions import BasePermission


class HasCustomPermission(BasePermission):
    """
    检查用户是否拥有指定的自定义权限
    """

    def __init__(self, required_permission):
        self.required_permission = required_permission

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.has_custom_permission(self.required_permission)


class IsAdminRole(permissions.BasePermission):
    """允许超级管理员或具有管理员角色的用户访问"""

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        # ✅ 兼容 Django createsuperuser
        if user.is_superuser:
            return True
        # ✅ 兼容自定义超级管理员（roles.filter(role_name="superadmin")）
        if hasattr(user, "is_super_admin") and user.is_super_admin():
            return True
        # ✅ 兼容普通管理员角色
        if hasattr(user, "is_admin") and user.is_admin():
            return True
        return False