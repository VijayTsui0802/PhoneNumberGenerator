from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NumberViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'numbers', NumberViewSet)
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]
