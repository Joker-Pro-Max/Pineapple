import requests
from django.conf import settings
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from utensil import generics
from utensil.views import CustomPagination
from .authentication import CustomTokenObtainPairSerializer
from .filters import UserFilter, SystemFilter, RoleFilter, CustomPermissionFilter
from .models import User, CustomPermission, System, Role
from .permissions import IsAdminRole
from .serializers import (
    RegisterSerializer, CustomTokenObtainPairSerializer, UserDetailSerializer, CustomPermissionSerializer,
    SystemSerializer, SystemCreateSerializer, SystemListRetrieveSerializer, PermissionCreateSerializer,
    PermissionListRetrieveSerializer, RoleListRetrieveSerializer, RoleCreateSerializer, UserUpdateSerializer,
    UserListSerializer, UserRetrieveSerializer
)


# ✅ 用户注册

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "user": self.get_serializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })


# ✅ 登录（使用 SimpleJWT 自定义序列化器）
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ✅ 刷新 Token（使用 SimpleJWT 内置）
class RefreshTokenView(TokenRefreshView):
    pass


# ✅ 微信登录（签发 SimpleJWT Token）
class WeChatLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):  # noqa
        code = request.data.get("code")
        if not code:
            return Response({"error": "Missing code"}, status=400)

        # ✅ 调用微信 API 获取 openid
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": settings.WX_APPID,
            "secret": settings.WX_SECRET,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        res = requests.get(url, params=params).json()
        openid = res.get("openid")
        unionid = res.get("unionid")  # noqa

        if not openid:
            return Response({"error": "WeChat auth failed"}, status=400)

        # ✅ 查找或创建用户
        user = User.objects.filter(wx_unionid=unionid).first() or User.objects.filter(wx_openid=openid).first()
        if not user:
            user = User.objects.create(username=f"wx_{openid[:6]}", wx_openid=openid, wx_unionid=unionid)

        # ✅ 使用 SimpleJWT 自定义 Token 生成
        serializer = CustomTokenObtainPairSerializer()
        token = serializer.get_token(user)
        return Response({"access": str(token.access_token), "refresh": str(token)})  # noqa


class UserListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserListSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter  # noqa
    queryset = User.objects.filter(is_deleted=False).order_by('-create_at')

class UserRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.filter(is_deleted=False).order_by('-create_at')
    serializer_class = UserRetrieveSerializer
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(self.msg(code=200, msg="成功", data=serializer.data))


class UserUpdateView(generics.UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserUpdateSerializer
    queryset = User.objects.filter(is_deleted=False)


# # ✅ 获取当前用户的全部信息
class CurrentUserView(generics.GenericAPIView):
    """
    获取当前登录用户详细信息（含角色、权限、系统、是否超级管理员）
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):  # noqa
        user = request.user

        # ✅ 获取用户所有权限（去重）
        permissions = CustomPermission.objects.filter(  # noqa
            roles__users=user,
            roles__is_enable=True
        ).distinct()

        # ✅ 获取用户关联系统（可选：如果 role → system 关联）
        systems = System.objects.filter(
            role__users=user
        ).distinct() if hasattr(Role, "system") else []

        data = {
            "user": UserDetailSerializer(user).data,
            "permissions": CustomPermissionSerializer(permissions, many=True).data,
            "systems": SystemSerializer(systems, many=True).data if systems else [],
        }

        return Response(self.msg(code=200, msg="成功", data=data))


# ✅ 系统 创建
class SystemCreateView(generics.CreateAPIView):  # noqa
    permission_classes = [permissions.AllowAny, IsAdminRole]
    serializer_class = SystemCreateSerializer


# ✅ 系统 列表
class SystemListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    serializer_class = SystemListRetrieveSerializer
    queryset = System.objects.filter(is_deleted=False).order_by("-create_at")
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = SystemFilter  # noqa


# ✅ 系统 详情 ｜ 修改
class SystemRetrieveView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    serializer_class = SystemListRetrieveSerializer
    queryset = System.objects.filter(is_deleted=False).order_by("-create_at")


# ✅ 系统 删除
class SystemDeleteView(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = System.objects.all()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.del_time = timezone.now()
        instance.save()
        return instance

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        deleted_uuid = instance.uuid  # 获取被删除对象的ID
        self.perform_destroy(instance)  # 执行删除

        # 自定义响应
        return Response(
            {
                "detail": f"{instance.system_name} 已删除",
                "deleted_id": deleted_uuid,
                "status": status.HTTP_200_OK
            },
            status=status.HTTP_200_OK  # 改用 200 OK 包含响应体
        )


# ✅ 系统 取消删除
class SystemCancelDeleteView(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = System.objects.all()

    def perform_destroy(self, instance):
        instance.is_deleted = False
        instance.save()
        return instance

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        deleted_uuid = instance.uuid  # 获取被删除对象的ID
        self.perform_destroy(instance)  # 执行删除

        # 自定义响应
        return Response(
            {
                "detail": f"{instance.system_name} 已恢复",
                "deleted_id": deleted_uuid,
                "status": status.HTTP_200_OK
            },
            status=status.HTTP_200_OK  # 改用 200 OK 包含响应体
        )


# ✅ 角色 创建
class RoleCreateView(generics.CreateAPIView):  # noqa
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    serializer_class = RoleCreateSerializer


# ✅ 角色 列表
class RoleListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    serializer_class = RoleListRetrieveSerializer
    queryset = Role.objects.filter(is_deleted=False).order_by("-create_at")
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RoleFilter  # noqa


# ✅ 角色 详情 ｜ 修改
class RoleRetrieveView(generics.RetrieveUpdateAPIView):  # noqa
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    serializer_class = RoleListRetrieveSerializer
    queryset = Role.objects.filter(is_deleted=False).order_by("-create_at")


# ✅ 角色 删除
class RoleDeleteView(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = Role.objects.all()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.del_time = timezone.now()
        instance.save()
        return instance

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        deleted_uuid = instance.uuid  # 获取被删除对象的ID
        self.perform_destroy(instance)  # 执行删除

        # 自定义响应
        return Response(
            {
                "detail": f"{instance.role_name} 已删除",
                "deleted_id": deleted_uuid,
                "status": status.HTTP_200_OK
            },
            status=status.HTTP_200_OK  # 改用 200 OK 包含响应体
        )


# ✅ 角色 取消删除
class RoleCancelDeleteView(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = Role.objects.all()

    def perform_destroy(self, instance):
        instance.is_deleted = False
        instance.save()
        return instance

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        deleted_uuid = instance.uuid  # 获取被删除对象的ID
        self.perform_destroy(instance)  # 执行删除

        # 自定义响应
        return Response(
            {
                "detail": f"{instance.role_name} 已恢复",
                "deleted_id": deleted_uuid,
                "status": status.HTTP_200_OK
            },
            status=status.HTTP_200_OK  # 改用 200 OK 包含响应体
        )


# ✅ 权限 创建
class PermissionCreateView(generics.CreateAPIView):  # noqa
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    serializer_class = PermissionCreateSerializer


# ✅ 权限 列表
class PermissionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    serializer_class = PermissionListRetrieveSerializer
    queryset = CustomPermission.objects.filter(is_deleted=False).order_by("-create_at")
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomPermissionFilter  # noqa


# ✅ 权限 详情 ｜ 修改
class PermissionRetrieveView(generics.RetrieveUpdateAPIView):  # noqa
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    serializer_class = PermissionListRetrieveSerializer
    queryset = CustomPermission.objects.filter(is_deleted=False).order_by("-create_at")


# ✅ 权限 删除
class PermissionDeleteView(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = CustomPermission.objects.all()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.del_time = timezone.now()
        instance.save()
        return instance

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        deleted_uuid = instance.uuid  # 获取被删除对象的ID
        self.perform_destroy(instance)  # 执行删除

        # 自定义响应
        return Response(
            {
                "detail": f"{instance.permission_name} 已删除",
                "deleted_id": deleted_uuid,
                "status": status.HTTP_200_OK
            },
            status=status.HTTP_200_OK  # 改用 200 OK 包含响应体
        )


# ✅ 权限 取消删除
class PermissionCancelDeleteView(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = CustomPermission.objects.all()

    def perform_destroy(self, instance):
        instance.is_deleted = False
        instance.save()
        return instance

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        deleted_uuid = instance.uuid  # 获取被删除对象的ID
        self.perform_destroy(instance)  # 执行删除

        # 自定义响应
        return Response(
            {
                "detail": f"{instance.permission_name} 已恢复",
                "deleted_id": deleted_uuid,
                "status": status.HTTP_200_OK
            },
            status=status.HTTP_200_OK  # 改用 200 OK 包含响应体
        )
