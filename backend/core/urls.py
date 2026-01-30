from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('machines', MachineViewSet)
router.register('pannes', PanneViewSet)
router.register('maintenances', MaintenanceViewSet)

urlpatterns = router.urls
