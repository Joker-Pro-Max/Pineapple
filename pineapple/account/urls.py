from django.urls import re_path

from .views import (
    LoginView, RegisterView, RefreshTokenView, WeChatLoginView, CurrentUserView, UserListView, UserUpdateView,
    SystemCreateView, SystemListView, SystemRetrieveView, SystemDeleteView, SystemCancelDeleteView, RoleCreateView,
    RoleListView, RoleRetrieveView, RoleDeleteView, RoleCancelDeleteView, PermissionCreateView, PermissionListView,
    PermissionRetrieveView, PermissionDeleteView, PermissionCancelDeleteView, UserRetrieveAPIView
)

urlpatterns = [
    re_path(r"^register/$", RegisterView.as_view()),
    re_path(r"^login/$", LoginView.as_view()),  # ✅ 颁发 Access / Refresh Token
    re_path(r"^refresh/$", RefreshTokenView.as_view()),  # ✅ 刷新 Access Token
    re_path(r"^wechat/$", WeChatLoginView.as_view()),  # ✅ 微信登录
    re_path(r"^myinfo/$", CurrentUserView.as_view()),  # ✅ 获取用户信息
    re_path(r"^user/list/$", UserListView.as_view()),  # ✅ 用户列表
    re_path(r"^user/(?P<pk>[0-9A-Za-z_-]{22})/$", UserRetrieveAPIView.as_view()),  # ✅ 用户详情
    re_path(r"^userinfo/(?P<pk>[0-9A-Za-z_-]{22})/update/$", UserUpdateView.as_view()),  # ✅ 修改用户信息

    # ✅ 系统 API
    re_path(r"^systems/create/$", SystemCreateView.as_view(), name="system-create"),
    re_path(r"^systems/list/$", SystemListView.as_view(), name="system-list"),
    re_path(r"^systems/(?P<pk>[0-9A-Za-z_-]{22})/$", SystemRetrieveView.as_view(), name="system-detail-update"),
    re_path(r"^systems/(?P<pk>[0-9A-Za-z_-]{22})/del/$", SystemDeleteView.as_view(), name="system-del"),
    re_path(r"^systems/(?P<pk>[0-9A-Za-z_-]{22})/cancel-del/$", SystemCancelDeleteView.as_view(),
            name="system-cancel-del"),

    # ✅ 角色 API
    re_path(r"^role/create/$", RoleCreateView.as_view(), name="role-create"),
    re_path(r"^role/list/$", RoleListView.as_view(), name="role-list"),
    re_path(r"^role/(?P<pk>[0-9A-Za-z_-]{22})/$", RoleRetrieveView.as_view(), name="role-detail-update"),
    re_path(r"^role/(?P<pk>[0-9A-Za-z_-]{22})/del/$", RoleDeleteView.as_view(), name="role-del"),
    re_path(r"^role/(?P<pk>[0-9A-Za-z_-]{22})/cancel-del/$", RoleCancelDeleteView.as_view(),
            name="role-cancel-del"),

    # ✅ 权限 API
    re_path(r"^permission/create/$", PermissionCreateView.as_view(), name="permission-create"),
    re_path(r"^permission/list/$", PermissionListView.as_view(), name="permission-list"),
    re_path(r"^permission/(?P<pk>[0-9A-Za-z_-]{22})/$", PermissionRetrieveView.as_view(),
            name="permission-detail-update"),
    re_path(r"^permission/(?P<pk>[0-9A-Za-z_-]{22})/del/$", PermissionDeleteView.as_view(), name="permission-del"),
    re_path(r"^permission/(?P<pk>[0-9A-Za-z_-]{22})/cancel-del/$", PermissionCancelDeleteView.as_view(),
            name="permission-cancel-del"),

]
