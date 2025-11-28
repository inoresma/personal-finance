from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, RecurringTransactionViewSet

router = DefaultRouter()
router.register('recurring', RecurringTransactionViewSet, basename='recurring')
router.register('', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
]







