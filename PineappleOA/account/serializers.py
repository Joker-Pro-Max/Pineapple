from rest_framework import serializers
from .models import (
    User, System, Role, CustomPermission
)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["unified_uuid", "uuid", "email", "phone", "username", "nickname", "all_roles", "all_permissions",
                  "password"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["unified_uuid", "uuid", "email", "phone", "username", "nickname", "all_roles", "all_permissions",
                  "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data  # ✅ 返回用户信息
        return data


class SystemSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)  # 显示用户名

    class Meta:
        model = System
        fields = ["uuid", "system_name", "system_code", "created_by", "create_at", "update_at"]


class RoleSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    permissions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # 如果需要权限 ID

    class Meta:
        model = Role
        fields = ["uuid", "role_name", "is_enable", "permissions", "created_by", "create_at", "update_at"]


# 获取用户详细信息
class CustomPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = ["uuid", "permission_name", "permission_code"]


class RoleUserSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    _existing_instance = None

    class Meta:
        model = Role
        fields = ["uuid", "role_name", "is_enable", "created_by", "permissions"]

    def validate(self, attrs):
        role_name = attrs.get("role_name")
        if role_name:
            try:
                existing = Role.objects.get(role_name=role_name)
                self._existing_instance = existing
                return attrs
            except Role.DoesNotExist:
                pass
        return attrs

    def create(self, validated_data):
        if self._existing_instance is not None:
            return self._existing_instance
        obj = Role.objects.create(**validated_data)
        return obj

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SystemUserSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    _existing_instance = None  # 用于保存已存在的实例

    class Meta:
        model = System
        fields = ["uuid", "system_name", "system_code", "created_by"]

    def validate(self, attrs):
        system_code = attrs.get("system_code")
        if system_code:
            try:
                # 查询是否已存在
                existing = System.objects.get(system_code=system_code)
                self._existing_instance = existing
                # 直接跳过后续创建校验
                return attrs
            except System.DoesNotExist:
                pass
        return attrs

    def create(self, validated_data):
        # 如果之前已存在，直接返回，不创建新对象
        if self._existing_instance is not None:
            return self._existing_instance
        # 否则正常创建
        obj = System.objects.create(**validated_data)
        return obj

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    roles = RoleUserSerializer(many=True, read_only=True)
    is_super_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "uuid", "unified_uuid", "email", "phone", "username", "nickname",
            "wx_openid", "wx_unionid", "wx_nickname", "wx_avatar_url",
            "roles", "is_super_admin"
        ]

    def get_is_super_admin(self, obj):
        return obj.is_super_admin()
