from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, SecondaryCategoryViewSet

router = DefaultRouter()
router.register('secondary', SecondaryCategoryViewSet, basename='secondary-category')
router.register('', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]













