from rest_framework import viewsets, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User


from .serializers import ReadHackerNewsSerializer, WriteHackerNewsSerializer, ReadUserSerializer, WriteUserSerializer
from .models import HackerNews, User
from .permissions import IsAdminOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ReadUserSerializer
    pagination_class = None
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ("list", "retrieve"):
            return ReadUserSerializer
        return WriteUserSerializer


class NewsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["type", "title"]

    def get_queryset(self):
        if self.action in ("list", "retrieve"):
            return HackerNews.objects.select_related("owner")
        return HackerNews.objects.select_related("owner").filter(owner=self.request.user)

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ("list", "retrieve"):
            return ReadHackerNewsSerializer
        return WriteHackerNewsSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    