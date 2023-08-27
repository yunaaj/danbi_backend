from rest_framework import serializers
from .models import User

class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=16)
    pwd = serializers.CharField(max_length=16)
    team = serializers.CharField(max_length=16)