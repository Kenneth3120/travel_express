from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TowerInstance, Credential, ExecutionEnvironment, Auditlog

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user management with secure password handling."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password']
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def create(self, validated_data):
        """Create user with encrypted password."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'viewer')
        )
        return user

    def update(self, instance, validated_data):
        """Update user, handle password encryption if provided."""
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)

        password = validated_data.get('password')
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance


class AuditlogSerializer(serializers.ModelSerializer):
    """Serializer for audit log entries - fixed naming consistency."""
    
    class Meta:
        model = Auditlog
        fields = '__all__'


class TowerInstanceSerializer(serializers.ModelSerializer):
    """Serializer for Tower instances with secure password handling."""
    
    class Meta:
        model = TowerInstance
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }


class CredentialSerializer(serializers.ModelSerializer):
    """Serializer for credentials with secure password handling."""
    
    class Meta:
        model = Credential
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }


class ExecutionEnvironmentSerializer(serializers.ModelSerializer):
    """Serializer for execution environments."""
    
    class Meta:
        model = ExecutionEnvironment
        fields = '__all__'