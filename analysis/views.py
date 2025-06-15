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

from ai_engine.pipeline import run as run_pipeline
from analysis.models import Entity, Angle, DatasetSuggestion





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

        # Appel du moteur IA (LangChain / pipeline)
        (
            packaged,
            markdown,
            score,
            _keywords_result,  # on ignore pour l'instant
            datasets,
        ) = run_pipeline(article.content, user_id=str(request.user.id))

        # Création de l’analyse avec score réel (summary = markdown de run_pipeline)
        analysis = Analysis.objects.create(
            article=article,
            summary=markdown,
            score=score,
        )

        # --------- ENTITIES ---------
        for person in packaged.extraction.persons:
            Entity.objects.create(
                analysis=analysis,
                type="PER",
                value=person,
                context=None,
            )
        for org in packaged.extraction.organizations:
            Entity.objects.create(
                analysis=analysis,
                type="ORG",
                value=org,
                context=None,
            )
        for loc in packaged.extraction.locations:
            Entity.objects.create(
                analysis=analysis,
                type="LOC",
                value=loc,
                context=None,
            )
        for date in packaged.extraction.dates:
            Entity.objects.create(
                analysis=analysis,
                type="DATE",
                value=date,
                context=None,
            )
        for num in packaged.extraction.numbers:
            Entity.objects.create(
                analysis=analysis,
                type="NUM",
                value=str(num.value) if hasattr(num, "value") else str(num),
                context=None,
            )

        # --------- ANGLES ---------
        for idx, ang in enumerate(packaged.angles.angles):
            Angle.objects.create(
                analysis=analysis,
                title=ang.title,
                description=ang.rationale,
                order=idx,
            )

        # --------- DATASETS — création en base -------------------------
        # NOUVEAU : on persiste chaque jeu de données trouvé par les connecteurs
        for ds in datasets:
            DatasetSuggestion.objects.create(
                analysis       = analysis,
                title          = ds.title,
                description    = ds.description or "",
                link           = ds.source_url,    # 🔁 nom légèrement différent
                source         = ds.source_name,
                found_by       = "CONNECTOR",
                formats        = ds.formats,
                organisation   = getattr(ds, "organization", None),
                licence        = ds.license,
                last_modified  = ds.last_modified or "",
                richness       = ds.richness or 0,
            )



        # --------- DATASETS (pas stockés en DB pour l'instant) ---------
        response_payload = {
            "message": "Analyse réussie",
            "article_id": article.id,
            "analysis_id": analysis.id,
            "datasets": [
                
                {
                    "title": d.title,
                    "description": d.description,
                    "source_name": d.source_name,
                    "source_url": d.source_url,
                    "formats": d.formats,
                    "license": d.license,
                    "organization": d.organization,
                    "last_modified": d.last_modified,
                    "richness": d.richness,
                }
                
                for d in datasets
            ],
        }

        return Response(response_payload, status=status.HTTP_201_CREATED)


# ---------- History ----------
class HistoryAPIView(generics.ListAPIView):
    """
    GET /history/   -> liste des analyses de l'utilisateur
    """
    serializer_class = AnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Analysis.objects.filter(article__user=self.request.user).order_by("-created_at")
