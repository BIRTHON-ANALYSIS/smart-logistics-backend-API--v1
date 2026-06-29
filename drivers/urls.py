from django.urls import path
from .views import DriverListCreateView, DriverDetailView

urlpatterns = [
    path('', DriverListCreateView.as_view(), name='driver-list'),
    path('<int:pk>/', DriverDetailView.as_view(), name='driver-detail'),
]

