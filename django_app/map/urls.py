from django.urls import path
from . import views

urlpatterns = [
    path("googlec2b4a3ec3165f0c3.html", views.serve_google_verification_file, name="google_verification"),
    path("", views.map_view, name="map"),
]