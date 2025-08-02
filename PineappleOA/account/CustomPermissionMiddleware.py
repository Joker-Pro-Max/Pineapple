import logging
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.models import CustomPermission

logger = logging.getLogger(__name__)

class CustomPermissionMiddleware:
    """
    自定义权限中间件（支持系统级权限 + 日志记录）：
    - Header: X-System-Code (系统标识)
    - Header: X-Required-Permission (权限码，支持多个逗号分隔)
    - Header: X-Permission-Logic (AND / OR，默认 OR)
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        system_code = request.headers.get("X-System-Code")
        required_perms_header = request.headers.get("X-Required-Permission")

        # 如果未配置权限验证头，直接放行
        if not (system_code and required_perms_header):
            logger.info(f"[PERMISSION] {request.method} {request.path} → 无权限要求，直接放行")
            return self.get_response(request)

        required_perms = [p.strip() for p in required_perms_header.split(",") if p.strip()]
        logic = request.headers.get("X-Permission-Logic", "OR").upper()

        # 认证 JWT
        try:
            user_auth_tuple = self.jwt_auth.authenticate(request)
            if user_auth_tuple is None:
                logger.warning(f"[PERMISSION] {request.method} {request.path} → 未认证访问")
                return JsonResponse({"detail": "未认证"}, status=401)
            user, _ = user_auth_tuple
            request.user = user
        except Exception as e:
            logger.error(f"[PERMISSION] {request.method} {request.path} → Token 无效: {e}")
            return JsonResponse({"detail": "无效的 Token"}, status=401)

        # 超级管理员绕过校验
        if hasattr(user, "is_super_admin") and user.is_super_admin():
            logger.info(f"[PERMISSION] {request.method} {request.path} → 超级管理员 {user.nickname} 访问放行")
            return self.get_response(request)

        # 权限验证
        if not self.check_user_system_permissions(user, system_code, required_perms, logic):
            logger.warning(
                f"[PERMISSION] {request.method} {request.path} → 用户 {user.nickname} "
                f"无权限（系统: {system_code}, 需要: {required_perms}, 逻辑: {logic})"
            )
            return JsonResponse({"detail": "权限不足"}, status=403)

        logger.info(
            f"[PERMISSION] {request.method} {request.path} → 用户 {user.nickname} 权限验证通过 "
            f"（系统: {system_code}, 权限: {required_perms}, 逻辑: {logic})"
        )
        return self.get_response(request)

    def check_user_system_permissions(self, user, system_code, permissions, logic="OR"):
        """
        检查用户在指定系统下是否具备所需权限
        """
        user_perms = CustomPermission.objects.filter(
            roles__users=user,
            roles__is_enable=True,
            roles__system__system_code=system_code,
            permission_code__in=permissions
        ).values_list("permission_code", flat=True).distinct()

        user_perm_set = set(user_perms)
        required_perm_set = set(permissions)

        if logic == "AND":
            return required_perm_set.issubset(user_perm_set)
        return bool(user_perm_set.intersection(required_perm_set))
