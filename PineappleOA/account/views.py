from rest_framework import permissions, status
from django.shortcuts import get_object_or_404

from utensil import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User, CustomPermission, System, Role
from .permissions import IsAdminRole
from .serializers import (
    RegisterSerializer, CustomTokenObtainPairSerializer, UserDetailSerializer, CustomPermissionSerializer,
    SystemSerializer, RoleUserSerializer, SystemUserSerializer
)
from .authentication import CustomTokenObtainPairSerializer
import requests
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


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


# 获取当前用户的全部信息
class CurrentUserView(generics.GenericAPIView):
    """
    获取当前登录用户详细信息（含角色、权限、系统、是否超级管理员）
    """
    permission_classes = [IsAuthenticated]

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

        return Response(data)


# ✅ 系统列表 + 创建
class SystemListCreateView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get(self, request):
        """系统列表"""
        systems = System.objects.all().order_by("-create_at")
        return Response(self.msg(code=200, msg="成功", data=SystemUserSerializer(systems, many=True).data))

    def post(self, request):
        """新增系统"""
        serializer = SystemUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(self.msg(code=200, msg="成功", data=serializer.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ 系统详情（修改 / 删除 / 详情）
class SystemDetailView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get_object(self, pk):  # noqa
        return get_object_or_404(System, pk=pk)

    def get(self, request, pk):
        """查看系统详情"""
        system = self.get_object(pk)
        return Response(SystemUserSerializer(system).data)

    def put(self, request, pk):
        """修改系统"""
        system = self.get_object(pk)
        serializer = SystemUserSerializer(system, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(self.msg(code=200, msg="成功", data=serializer.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """软删除系统"""
        system = self.get_object(pk)
        system.is_deleted = True
        system.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ✅ 角色列表 + 创建
class RoleListCreateView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get(self, request):  # noqa
        """角色列表"""
        roles = Role.objects.all().order_by("-create_at")
        return Response(RoleUserSerializer(roles, many=True).data)

    def post(self, request):
        """新增角色"""
        serializer = RoleUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ 角色详情（修改 / 删除 / 详情）
class RoleDetailView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get_object(self, pk):  # noqa
        return get_object_or_404(Role, pk=pk)

    def get(self, request, pk):
        """查看角色详情"""
        role = self.get_object(pk)
        return Response(RoleUserSerializer(role).data)

    def put(self, request, pk):
        """修改角色"""
        role = self.get_object(pk)
        serializer = RoleUserSerializer(role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """软删除角色"""
        role = self.get_object(pk)
        role.is_deleted = True
        role.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
