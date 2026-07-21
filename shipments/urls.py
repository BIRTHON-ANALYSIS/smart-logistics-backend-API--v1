from django.urls import path
from .views import AssignDriverView, ShipmentHistoryView, ShipmentListCreateView, ShipmentStatusUpdateView, ShipmentUpdateView, ShipmentDetailView, TrackShipmentView



urlpatterns = [
    path('', ShipmentListCreateView.as_view()),
    path('track/<str:tracking_number>/', TrackShipmentView.as_view(), name='track-shipment'),
    path('<int:pk>/', ShipmentDetailView.as_view()),
    path('<int:pk>/update/', ShipmentUpdateView.as_view()),
    path('<int:pk>/status/', ShipmentStatusUpdateView.as_view(), name='shipment-status-update'),
    path('<int:pk>/assign-driver/', AssignDriverView.as_view(), name='assign-driver'),
    path( "<str:tracking_number>/history/",  ShipmentHistoryView.as_view(),
    name="shipment-history",
),
    
]

