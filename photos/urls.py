from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PhotoViewSet, PhotographerViewSet

router = DefaultRouter()
router.register(r'photos', PhotoViewSet, basename='photos')
router.register(r'photographers', PhotographerViewSet, basename='photographers')

app_name = 'photos'

urlpatterns = [
    path('', include(router.urls)),
]