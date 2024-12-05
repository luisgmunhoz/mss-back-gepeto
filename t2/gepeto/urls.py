from django.urls import path
from .views import HealthAssistantView

urlpatterns = [
    path("health-assistant/", HealthAssistantView.as_view(), name="health-assistant"),
]
