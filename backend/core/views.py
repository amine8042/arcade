from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError

from .models import User, MachineArcade, Panne, Maintenance
from .serializers import (
    UserSerializer,
    MachineSerializer,
    PanneSerializer,
    MaintenanceSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        role = serializer.validated_data.get('role')
        if role == 'ADMIN' and User.objects.filter(role='ADMIN').exists():
            raise ValidationError("Un seul Admin autorisé.")
        serializer.save()


class MachineViewSet(viewsets.ModelViewSet):
    queryset = MachineArcade.objects.all()
    serializer_class = MachineSerializer
    permission_classes = [permissions.IsAuthenticated]


class PanneViewSet(viewsets.ModelViewSet):
    queryset = Panne.objects.all()
    serializer_class = PanneSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = [permissions.IsAuthenticated]
