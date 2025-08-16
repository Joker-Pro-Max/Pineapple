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


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["uuid", "email", "phone", "username", "nickname", "wx_nickname", "wx_avatar_url"]

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["phone", "avatar", "username", "nickname"]




class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["uuid", "email", "phone", "username", "nickname"]


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


class UserDetailSerializer(serializers.ModelSerializer):
    roles = RoleUserSerializer(many=True, read_only=True)
    is_super_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "uuid", "unified_uuid", "email", "phone", "username", "nickname",
            "wx_openid", "wx_unionid", "wx_nickname", "wx_avatar_url",  # noqa
            "roles", "is_super_admin"
        ]

    def get_is_super_admin(self, obj):  # noqa
        return obj.is_super_admin()


class CustomPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermission
        fields = ["uuid", "permission_name", "permission_code"]


# ✅ 用户信息-创建者
class UserCreatedBYSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["nickname", "uuid", "unified_uuid", "nickname", "wx_nickname"]


# ✅ 系统 创建
class SystemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = System
        fields = [
            "system_code", "system_name"
        ]

    def create(self, validated_data):
        created_by = self.context["request"].user
        validated_data['created_by'] = created_by
        system_code = validated_data['system_code']
        system_name = validated_data['system_name']

        system_obj = self.Meta.model.objects.filter(
            system_code=system_code,
            system_name=system_name,
            is_deleted=False
        ).first()
        if not system_obj:
            return self.Meta.model.objects.create(**validated_data)
        return system_obj


# ✅ 系统 详情 | 列表 | 修改
class SystemListRetrieveSerializer(serializers.ModelSerializer):
    created_info = UserCreatedBYSerializer(source="created_by", read_only=True)

    class Meta:
        model = System
        fields = [
            "uuid", "system_code", "system_name", "created_info"
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# ✅ 角色  创建
class RoleCreateSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Role
        fields = [
            "role_name"
        ]

    def create(self, validated_data):
        created_by = self.context["request"].user
        role_name = validated_data['role_name']
        validated_data['created_by'] = created_by
        role_obj = self.Meta.model.objects.filter(
            role_name=role_name,
            created_by=created_by,
            is_deleted=False
        ).first()
        if not role_obj:
            return self.Meta.model.objects.create(**validated_data)
        return role_obj


# ✅ 角色 详情 | 列表 | 修改
class RoleListRetrieveSerializer(serializers.ModelSerializer):
    created_info = UserCreatedBYSerializer(source="created_by", read_only=True)

    class Meta:
        model = Role
        fields = [
            "uuid", "role_name", "created_info"
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# ✅ 权限  创建
class PermissionCreateSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = CustomPermission
        fields = [
            "permission_name", "permission_code"
        ]

    def create(self, validated_data):
        created_by = self.context["request"].user
        validated_data['created_by'] = created_by
        permission_name = validated_data['permission_name']
        permission_code = validated_data['permission_code']

        permission_obj = self.Meta.model.objects.filter(
            permission_name=permission_name,
            permission_code=permission_code,
            is_deleted=False
        ).first()
        if not permission_obj:
            return self.Meta.model.objects.create(**validated_data)
        return permission_obj


# ✅ 权限 详情 | 列表 | 修改
class PermissionListRetrieveSerializer(serializers.ModelSerializer):
    created_info = UserCreatedBYSerializer(source="created_by", many=False, read_only=True)

    class Meta:
        model = CustomPermission
        fields = [
            "uuid", "permission_name", "permission_code", "created_info"
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
