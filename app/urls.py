# backend/app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NumberViewSet

router = DefaultRouter()
router.register(r'numbers', NumberViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
