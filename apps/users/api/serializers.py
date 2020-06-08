from rest_framework import serializers

from apps.users.models import User


class MiniprogramLoginSerializer(serializers.Serializer):

    code = serializers.CharField()
    avatar = serializers.CharField()
    name = serializers.CharField()
    encryptedData = serializers.CharField()
    iv = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    """web/api登陆
    """

    username = serializers.CharField()
    password = serializers.CharField(required=False)
    code = serializers.CharField(max_length=4, required=False)


class BindPhoneSerializer(serializers.Serializer):
    """绑定手机号
    """
    id_card = serializers.CharField()
    name = serializers.CharField()
    phone = serializers.CharField()
    code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'avatar', 'name', 'is_superuser']


class UserInlineSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'avatar', 'name']


class UserProfileSerializer(serializers.ModelSerializer):
    
    avatar = serializers.CharField(allow_blank=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'name', 'is_superuser',]
        read_only_fields = ['username', 'is_superuser',]


class GetCodeSerializer(serializers.Serializer):

    phone = serializers.CharField(max_length=11)
