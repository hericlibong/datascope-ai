import logging
import time
from analysis.models import Analysis, Article, Entity, Angle, DatasetSuggestion
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.db import transaction
from rest_framework import status
from django.conf import settings
from analysis.views import ArticleViewSet, AnalysisViewSet, HistoryAPIView
from users.views import FeedbackViewSet

from ai_engine.pipeline import run as run_pipeline
from analysis.serializers import AnalysisDetailSerializer, AngleResourcesSerializer

from django.contrib.auth import get_user_model

logger = logging.getLogger("playground")

def _get_playground_user():
    User = get_user_model()
    user, _ = User.objects.get_or_create(
        username="playground",
        defaults={"email": "playground@example.com"}
    )
    return user

class PlaygroundDebugMixin:
    """
    Injection _debug automatique dès que ?debug=1 est présent, pour TOUTES
    les réponses des vues Playground (list/retrieve/create/update...).
    Ajoute aussi timing & compteurs simples.
    """

    def initial(self, request, *args, **kwargs):
        # point de départ pour le timing
        self._ts_playground = time.perf_counter()
        return super().initial(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        # Logging sortie "classique"
        try:
            out_size = len(str(getattr(response, "data", "")))
        except Exception:
            out_size = None
        logger.debug({"status": response.status_code, "payload_out_size": out_size})

        # Injection _debug automatique si demandé et si payload JSON dict
        try:
            if request.query_params.get("debug") == "1" and hasattr(response, "data") and isinstance(response.data, dict):
                try:
                    dur_ms = int((time.perf_counter() - getattr(self, "_ts_playground", 0)) * 1000)
                except Exception:
                    dur_ms = None

                # user id safe
                if getattr(request.user, "is_authenticated", False):
                    user_id = request.user.id
                else:
                    user_id = None

                # compteurs si dispos
                d = response.data
                counts = {}
                for key in ("entities", "angles", "datasets", "angle_resources"):
                    if key in d and isinstance(d[key], list):
                        counts[f"{key}_count"] = len(d[key])

                # section/action indicative
                section = getattr(self, "debug_section", None)
                if not section:
                    # fallback sur le nom de la classe + action DRF si dispo
                    action = getattr(self, "action", None)
                    section = f"{self.__class__.__name__}:{action or 'unknown'}"

                d["_debug"] = {
                    "section": section,
                    "path": request.get_full_path(),
                    "method": request.method,
                    "user": user_id,
                    "duration_ms": dur_ms,
                    **counts,
                }
                response.data = d
        except Exception:
            # on ne casse jamais la réponse si la partie _debug échoue
            pass

        return super().finalize_response(request, response, *args, **kwargs)
    
    def _maybe_debug(self, request, data, meta=None):
        """Compat legacy: les vues qui appellent encore _maybe_debug ne cassent pas.
        L'injection _debug est désormais faite dans finalize_response()."""
        return data



class ArticlePlaygroundViewSet(PlaygroundDebugMixin, ArticleViewSet):
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if getattr(self.request.user, "is_authenticated", False) else _get_playground_user()
        serializer.save(user=user)
    
    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        data = getattr(resp, "data", {})
        meta = {"section": "articles/create"}
        resp.data = self._maybe_debug(request, data, meta)
        return resp


class AnalysisPlaygroundViewSet(PlaygroundDebugMixin, AnalysisViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if not getattr(user, "is_authenticated", False):
            return Analysis.objects.filter(article__user__username="playground").order_by("-created_at")
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        # user playground si anonyme
        if not getattr(request.user, "is_authenticated", False):
            request.user = _get_playground_user()

        # 1) article
        article_id = request.data.get("article")
        if not article_id:
            return Response({"article": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({"article": ["Invalid article id."]}, status=status.HTTP_400_BAD_REQUEST)

        # 2) pipeline with validation flag
        validate_qs = (request.query_params.get("validate") or "").strip().lower()
        validate_flag = validate_qs in ("1", "true", "yes", "on")
        if not validate_qs:
            # fallback global si le front n'envoie pas le paramètre
            validate_flag = bool(getattr(settings, "URL_VALIDATION_DEFAULT", True))

        packaged, markdown, score, angle_resources = run_pipeline(
            article.content,
            user_id=str(request.user.id),
            validate_urls=validate_flag,
        )
        angle_resources_payload = AngleResourcesSerializer(angle_resources, many=True).data

        # 3) upsert (create or update)
        with transaction.atomic():
            analysis, created = Analysis.objects.get_or_create(
                article=article,
                defaults={
                    "summary": markdown,
                    "score": score,
                    "angle_resources": angle_resources_payload,
                    "profile_label": request.data.get("profile_label", "playground"),
                },
            )
            if not created:
                # purge des anciens détails
                Entity.objects.filter(analysis=analysis).delete()
                Angle.objects.filter(analysis=analysis).delete()
                DatasetSuggestion.objects.filter(analysis=analysis).delete()
                # mise à jour des champs principaux
                analysis.summary = markdown
                analysis.score = score
                analysis.angle_resources = angle_resources_payload
                analysis.profile_label = request.data.get("profile_label", "playground")
                analysis.save()

            # 4) ENTITIES
            for person in packaged.extraction.persons:
                Entity.objects.create(analysis=analysis, type="PER", value=person)
            for org in packaged.extraction.organizations:
                Entity.objects.create(analysis=analysis, type="ORG", value=org)
            for loc in packaged.extraction.locations:
                Entity.objects.create(analysis=analysis, type="LOC", value=loc)
            for date in packaged.extraction.dates:
                Entity.objects.create(analysis=analysis, type="DATE", value=date)
            for num in packaged.extraction.numbers:
                Entity.objects.create(analysis=analysis, type="NUM", value=str(getattr(num, "value", num)))

            # 5) ANGLES
            for idx, ang in enumerate(packaged.angles.angles):
                Angle.objects.create(
                    analysis=analysis,
                    title=ang.title,
                    description=getattr(ang, "rationale", "") or getattr(ang, "description", ""),
                    order=idx,
                )

            # 6) DATASETS
            for ar in angle_resources:
                for ds in ar.datasets:
                    DatasetSuggestion.objects.create(
                        analysis=analysis,
                        title=ds.title,
                        description=ds.description or "",
                        link=ds.source_url or ds.link,
                        source=ds.source_name,
                        found_by=ds.found_by,
                        formats=ds.formats,
                        organisation=getattr(ds, "organization", None),
                        licence=ds.license,
                        last_modified=ds.last_modified or "",
                        richness=ds.richness or 0,
                    )

        # 7) réponse
        data = AnalysisDetailSerializer(analysis).data
        data = self._maybe_debug(request, data, {"section": "analysis/create", "upsert": (not created)})
        return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)





    def retrieve(self, request, *args, **kwargs):
        resp = super().retrieve(request, *args, **kwargs)
        data = getattr(resp, "data", {})
        meta = {"section": "analysis/retrieve"}
        resp.data = self._maybe_debug(request, data, meta)
        return resp

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        # liste → pas d’injection _debug pour éviter de gonfler les payloads,
        # mais on logge l’appel
        logger.debug({"section": "analysis/list"})
        return resp


class FeedbackPlaygroundViewSet(PlaygroundDebugMixin, FeedbackViewSet):
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        data = getattr(resp, "data", {})
        meta = {"section": "feedback/create"}
        resp.data = self._maybe_debug(request, data, meta)
        return resp


class HistoryPlaygroundAPIView(PlaygroundDebugMixin, HistoryAPIView):
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if not getattr(user, "is_authenticated", False):
            return Analysis.objects.none()
        return super().get_queryset()

    def get(self, request, *args, **kwargs):
        resp = super().get(request, *args, **kwargs)
        data = getattr(resp, "data", {})
        meta = {"section": "history/get"}
        if isinstance(resp, Response) and isinstance(data, dict):
            resp.data = self._maybe_debug(request, data, meta)
        return resp

