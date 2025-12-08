from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportView.as_view(), name='reports'),
    path('dashboard/', views.ReportView.as_view(), name='dashboard'),
    path('by_secondary_category/', views.SecondaryCategoryReportView.as_view(), name='by_secondary_category'),
    path('category-trend/', views.CategoryTrendView.as_view(), name='category_trend'),
    path('habits-analysis/', views.HabitsAnalysisView.as_view(), name='habits_analysis'),
]
