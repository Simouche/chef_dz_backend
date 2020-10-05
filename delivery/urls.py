from django.urls import path

from . import views

url_patterns = [
    path("delivery/create/", views.DeliveryCreateView.as_view()),
    path("delivery/update/<int:pk>/", views.DeliveryUpdateView),
    path("delivery/delete/<int:pk>/", views.DeliveryDeleteView),
    path("delivery/track/", views.DeliveryTracksView),
]
