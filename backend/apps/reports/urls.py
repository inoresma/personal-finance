from django.urls import path
from .views import DashboardView, ReportsView, ExportView, ImportView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('exportar/', ExportView.as_view(), name='export'),
    path('import/', ImportView.as_view(), name='import'),
    path('', ReportsView.as_view(), name='reports'),
]

