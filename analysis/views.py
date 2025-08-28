from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.timezone import now
from django.conf import settings

from .models import Article, Analysis
from .serializers import (
    ArticleSerializer,
    AnalysisSerializer,
    AnalysisDetailSerializer,
    AngleResourcesSerializer
)
# from users.serializers import FeedbackSerializer
# from users.models import Feedback

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
        file    = request.data.get("file")

        # --- contrôles minimalistes ---
        if not content and not file:
            return Response({"error_code": "empty_input"}, status=status.HTTP_400_BAD_REQUEST)

        if file:
            if not any(file.name.endswith(ext) for ext in (".txt", ".md")):
                return Response({"error_code": "invalid_file_type"}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
            if file.size > 2_000_000:
                return Response({"error_code": "file_too_large"}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        if content and len(content) < 10:
            return Response({"error_code": "text_too_short"}, status=status.HTTP_400_BAD_REQUEST)

        article = Article.objects.create(
            user=request.user,
            content=content if content else file.read().decode("utf-8"),
            submitted_at=now()
        )

        # ------------------------------------------------------------------
        # 1. Appel du pipeline (nouvelle signature)
        # ------------------------------------------------------------------

        # --- ✅ NEW: lecture du flag ?validate=true dans la query string ---
        # Exemples acceptés : ?validate=true / ?validate=1 / ?validate=yes / ?validate=on
        validate_qs = (request.query_params.get("validate") or "").strip().lower()  # NEW
        validate_flag = validate_qs in ("1", "true", "yes", "on")                    # NEW
        if not validate_qs:
            validate_flag = bool(getattr(settings, "URL_VALIDATION_DEFAULT", True))
        # -------------------------------------------------------------------

        (
            packaged,           # Extraction + angles (Pydantic)
            markdown,           # Résumé markdown
            score,              # Score final (0-10)
            angle_resources,    # list[AngleResources]
        ) = run_pipeline(
            article.content,
            user_id=str(request.user.id),
            validate_urls=validate_flag,   # ✅ NEW: active le hook de validation d’URL dans le pipeline
            # filter_404=None              # (optionnel) on laisse les settings piloter le filtrage
        )

        # ------------------------------------------------------------------
        # 2. Persistance de l’analyse
        # ------------------------------------------------------------------
        analysis = Analysis.objects.create(
            article = article,
            summary = markdown,
            score   = score,
            angle_resources = AngleResourcesSerializer(angle_resources, many=True).data
        )

        # --------- ENTITIES (idem avant) -------------------
        for person in packaged.extraction.persons:
            Entity.objects.create(analysis=analysis, type="PER",  value=person)
        for org in packaged.extraction.organizations:
            Entity.objects.create(analysis=analysis, type="ORG",  value=org)
        for loc in packaged.extraction.locations:
            Entity.objects.create(analysis=analysis, type="LOC",  value=loc)
        for date in packaged.extraction.dates:
            Entity.objects.create(analysis=analysis, type="DATE", value=date)
        for num in packaged.extraction.numbers:
            Entity.objects.create(
                analysis=analysis, type="NUM",
                value=str(getattr(num, "value", num))
            )

        # --------- ANGLES (idem avant) ----------------------
        for idx, ang in enumerate(packaged.angles.angles):
            Angle.objects.create(
                analysis   = analysis,
                title      = ang.title,
                description= ang.rationale,
                order      = idx,
            )

        # --------- DATASETS : on parcourt chaque angle --------------------
        created_count = 0
        for ar in angle_resources:
            for ds in ar.datasets:
                DatasetSuggestion.objects.create(
                    analysis       = analysis,
                    title          = ds.title,
                    description    = ds.description or "",
                    link           = ds.source_url or ds.link,
                    source         = ds.source_name,
                    found_by       = ds.found_by,
                    formats        = ds.formats,
                    organisation   = getattr(ds, "organization", None),
                    licence        = ds.license,
                    last_modified  = ds.last_modified or "",
                    richness       = ds.richness or 0,
                )
                created_count += 1
        print(f"[DEBUG] {created_count} DatasetSuggestion rows saved")

        # --------- RÉPONSE JSON ------------------------------------------
        payload = {
            "message"        : "Analyse réussie",
            "article_id"     : article.id,
            "analysis_id"    : analysis.id,
            "angle_resources": AngleResourcesSerializer(
                angle_resources, many=True
            ).data,
        }
        return Response(payload, status=status.HTTP_201_CREATED)


# ---------- History ----------
class HistoryAPIView(generics.ListAPIView):
    """
    GET /history/   -> liste des analyses de l'utilisateur
    """
    serializer_class = AnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Analysis.objects.filter(article__user=self.request.user).order_by("-created_at")
