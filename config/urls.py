
from django.contrib import admin
from django.urls import path,include
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


def home(request):
    return JsonResponse({
        "message": "Smart Logistics API is running"
    })


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/shipments/',include('shipments.urls') ),
    path('api/accounts/', include('accounts.urls')),
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/drivers/', include('drivers.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/tracking/', include('tracking.urls')),


]

