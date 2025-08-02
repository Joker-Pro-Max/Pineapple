from utensil import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User
from .serializers import (
    RegisterSerializer, CustomTokenObtainPairSerializer
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

    def post(self, request):
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
        unionid = res.get("unionid")

        if not openid:
            return Response({"error": "WeChat auth failed"}, status=400)

        # ✅ 查找或创建用户
        user = User.objects.filter(wx_unionid=unionid).first() or User.objects.filter(wx_openid=openid).first()
        if not user:
            user = User.objects.create(username=f"wx_{openid[:6]}", wx_openid=openid, wx_unionid=unionid)

        # ✅ 使用 SimpleJWT 自定义 Token 生成
        serializer = CustomTokenObtainPairSerializer()
        token = serializer.get_token(user)
        return Response({"access": str(token.access_token), "refresh": str(token)})
