from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义 JWT Payload，添加 roles & permissions
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token