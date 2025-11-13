from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Photo, Photographer
from .serializers import (
    PhotoSerializer,
    PhotoListSerializer,
    PhotoCreateSerializer,
    PhotographerSerializer,
    PhotographerListSerializer,
)


class PhotographerViewSet(viewsets.ModelViewSet):
    queryset = Photographer.objects.all()
    serializer_class = PhotographerSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["photographer_id"]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "photographer_id"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
            return PhotographerListSerializer
        return PhotographerSerializer

    @extend_schema(
        description="Get all photos by this photographer",
        responses={200: PhotoSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def photos(self, request, pk=None):
        photographer = self.get_object()
        photos = photographer.photos.all()
        serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data)


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.select_related("photographer").all()
    serializer_class = PhotoSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["photographer", "photo_id"]
    search_fields = ["photographer__name", "alt"]
    ordering_fields = ["id", "photo_id", "width", "height", "created_at"]
    ordering = ["-id"]

    def get_serializer_class(self):
        if self.action == "list":
            return PhotoListSerializer
        elif self.action == "create":
            return PhotoCreateSerializer
        return PhotoSerializer
