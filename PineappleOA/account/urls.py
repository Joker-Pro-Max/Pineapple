from django.urls import re_path

from .views import (
    RegisterView, LoginView, RefreshTokenView, WeChatLoginView, CurrentUserView, SystemListCreateView, SystemDetailView,
    RoleListCreateView, RoleDetailView
)

urlpatterns = [
    re_path(r"^register/$", RegisterView.as_view()),
    re_path(r"^login/$", LoginView.as_view()),  # ✅ 颁发 Access / Refresh Token
    re_path(r"^refresh/$", RefreshTokenView.as_view()),  # ✅ 刷新 Access Token
    re_path(r"^wechat/$", WeChatLoginView.as_view()),  # ✅ 微信登录
    re_path(r"^myinfo/$", CurrentUserView.as_view()),  # ✅ 获取用户信息

    re_path(r"^systems/$", SystemListCreateView.as_view(), name="system-list-create"),
    re_path(r"^systems/<int:pk>/$", SystemDetailView.as_view(), name="system-detail"),

    # 角色 API
    re_path(r"^roles/$", RoleListCreateView.as_view(), name="role-list-create"),
    re_path(r"^roles/<int:pk>/$", RoleDetailView.as_view(), name="role-detail"),
]
