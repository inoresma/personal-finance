from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/categories/', include('apps.categories.urls')),
    path('api/transactions/', include('apps.transactions.urls')),
    path('api/budgets/', include('apps.budgets.urls')),
    path('api/investments/', include('apps.investments.urls')),
    path('api/debts/', include('apps.debts.urls')),
    path('api/bets/', include('apps.bets.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/goals/', include('apps.goals.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
