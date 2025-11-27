from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvestmentViewSet

router = DefaultRouter()
router.register('', InvestmentViewSet, basename='investment')

urlpatterns = [
    path('', include(router.urls)),
]





