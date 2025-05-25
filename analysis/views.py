from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework import status

from .models import Article, Analysis
from .serializers import (
    ArticleSerializer,
    AnalysisSerializer,
    AnalysisDetailSerializer,
)
from users.serializers import FeedbackSerializer
from users.models import Feedback


class IsOwner(permissions.BasePermission):
    """Autorise l’accès aux objets appartenant à l’utilisateur courant."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


# ---------- Article ----------
class ArticleViewSet(viewsets.ModelViewSet):
    """
    POST /articles/   -> créer un article (content ou file)
    GET  /articles/   -> lister mes articles
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Article.objects.filter(user=self.request.user).order_by("-submitted_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------- Analysis ----------
class AnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /analysis/<id>/   -> détail complet (nested)
    """
    queryset = Analysis.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = "id"

    def get_queryset(self):
        return Analysis.objects.filter(article__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AnalysisDetailSerializer
        return AnalysisSerializer


# ---------- History ----------
class HistoryAPIView(generics.ListAPIView):
    """
    GET /history/   -> liste des analyses de l'utilisateur
    """
    serializer_class = AnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Analysis.objects.filter(article__user=self.request.user).order_by("-created_at")
