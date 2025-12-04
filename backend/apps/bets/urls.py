from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BetViewSet

router = DefaultRouter()
router.register('', BetViewSet, basename='bet')

urlpatterns = [
    path('', include(router.urls)),
]



