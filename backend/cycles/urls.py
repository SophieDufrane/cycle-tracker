from rest_framework.routers import DefaultRouter
from .views import CycleLogViewSet

router = DefaultRouter()
router.register("cycle-log", CycleLogViewSet, basename="cycle-log")

urlpatterns = router.urls