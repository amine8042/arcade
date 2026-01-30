from rest_framework import serializers
from .models import User, MachineArcade, Panne, Maintenance


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineArcade
        fields = '__all__'


class PanneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Panne
        fields = '__all__'
        read_only_fields = ['user', 'date_declaration']


class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = '__all__'
