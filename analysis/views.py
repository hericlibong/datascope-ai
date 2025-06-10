from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.timezone import now

from .models import Article, Analysis
from .serializers import (
    ArticleSerializer,
    AnalysisSerializer,
    AnalysisDetailSerializer,
)
from users.serializers import FeedbackSerializer
from users.models import Feedback


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Pour les analyses, l’auteur est sur l’article lié
        if hasattr(obj, "article"):
            return obj.article.user == request.user
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
    

class ArticleAnalyzeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        content = request.data.get("text")
        file = request.data.get("file")

        # -- Contrôles de validation sans messages explicites --
        if not content and not file:
            return Response({"error_code": "empty_input"}, status=status.HTTP_400_BAD_REQUEST)

        if file:
            allowed_extensions = [".txt", ".md"]
            if not any(file.name.endswith(ext) for ext in allowed_extensions):
                return Response({"error_code": "invalid_file_type"}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

            if file.size > 2_000_000:  # 2 Mo
                return Response({"error_code": "file_too_large"}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        if content and len(content) < 10:
            return Response({"error_code": "text_too_short"}, status=status.HTTP_400_BAD_REQUEST)
        

        article = Article.objects.create(
            user=request.user,
            content=content if content else file.read().decode("utf-8"),
            submitted_at=now()
        )

        # En vrai, logique NLP ici...
        analysis = Analysis.objects.create(
            article=article,
            summary="Résumé généré automatiquement",
            score=0.8,  # valeur fictive
        )

        return Response({
            "message": "Analyse réussie",
            "article_id": article.id,
            "analysis_id": analysis.id
        }, status=status.HTTP_201_CREATED)



# ---------- History ----------
class HistoryAPIView(generics.ListAPIView):
    """
    GET /history/   -> liste des analyses de l'utilisateur
    """
    serializer_class = AnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Analysis.objects.filter(article__user=self.request.user).order_by("-created_at")
    

