from django.urls import re_path

from .views import (
    RegisterView, LoginView, RefreshTokenView, WeChatLoginView
)

urlpatterns = [
    re_path(r"^register/$", RegisterView.as_view()),
    re_path(r"^login/$", LoginView.as_view()),  # ✅ 颁发 Access / Refresh Token
    re_path(r"^refresh/$", RefreshTokenView.as_view()),  # ✅ 刷新 Access Token
    re_path(r"^wechat/$", WeChatLoginView.as_view()),  # ✅ 微信登录

]
