from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义 JWT Payload，添加 roles & permissions
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # ✅ 额外字段
        token["roles"] = user.all_roles
        token["permissions"] = user.all_permissions
        return token