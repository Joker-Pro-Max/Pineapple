import django_filters
from django_filters import rest_framework as filters
from account.models import Role, User, System, CustomPermission


class UserFilter(django_filters.rest_framework.FilterSet):
    email = filters.CharFilter(lookup_expr='icontains')
    phone = filters.CharFilter(lookup_expr='icontains')
    username = filters.CharFilter(lookup_expr='icontains')
    nickname = filters.CharFilter(lookup_expr='icontains')
    wx_nickname = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = User
        fields = ["email", "phone", "username", "nickname", "wx_nickname"]


class SystemFilter(django_filters.rest_framework.FilterSet):
    system_name = filters.CharFilter(lookup_expr='icontains')
    system_code = filters.CharFilter(lookup_expr='icontains')
    created_by = django_filters.CharFilter(field_name="created_by__unified_uuid", lookup_expr="exact")

    class Meta:
        model = System
        fields = ["system_name", "system_code", "created_by"]


class RoleFilter(django_filters.rest_framework.FilterSet):
    role_name = filters.CharFilter(lookup_expr='icontains')
    is_enable = filters.BooleanFilter()
    created_by = django_filters.CharFilter(field_name="created_by__unified_uuid", lookup_expr="exact")

    class Meta:
        model = Role
        fields = ["role_name", "is_enable", "created_by"]


class CustomPermissionFilter(django_filters.rest_framework.FilterSet):
    permission_name = filters.CharFilter(lookup_expr='icontains')
    permission_code = filters.CharFilter(lookup_expr='icontains')
    created_by = django_filters.CharFilter(field_name="created_by__unified_uuid", lookup_expr="exact")

    class Meta:
        model = CustomPermission
        fields = ["permission_name", "permission_code", "created_by"]
