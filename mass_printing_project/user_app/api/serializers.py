from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from user_app.models import File,ExtractedData,ExtractedAdvisor


class RegistrationSerializer(serializers.ModelSerializer):
    
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password','password2')
        extra_kwargs = {
            'password': {
                'write_only': True,
               'style': {'input_type': 'password'}
            }
        }
    
    def save(self):
        email = self.validated_data['email']
        p1 = self.validated_data['password']
        p2 = self.validated_data['password2']

        if p1 != p2:
            raise ValidationError('Password mismatch')
        
        queryset = User.objects.filter(email=email)
        if queryset.exists():
            raise ValidationError('Email already exists')

        user = User(username=self.validated_data['username'],
                    email=self.validated_data['email'])
        user.set_password(self.validated_data['password'])
        user.save()
        return user


class FileSerializer(serializers.ModelSerializer):
    uploader = serializers.CharField(source='uploader.username', read_only=True)
    class Meta:
        model = File
        fields = '__all__'


class ExtractedDataSerializer(serializers.Serializer):
    class Meta:
        model = ExtractedData  
        fields='__all__'  

class ExtractAdvisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedAdvisor 
        fields='__all__'        