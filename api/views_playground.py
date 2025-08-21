import logging
from analysis.models import Analysis
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from analysis.views import ArticleViewSet, AnalysisViewSet, HistoryAPIView
from users.views import FeedbackViewSet

logger = logging.getLogger("playground")

class PlaygroundDebugMixin:
    """
    - Logge la requête + la réponse (statut, tailles, temps…)
    - Si query param `debug=1`, ajoute un champ `_debug` dans le payload de réponse
      (sans modifier le schéma principal consommé par l’UI normale).
    """
    def _add_debug(self, data, extra=None):
        try:
            if isinstance(data, dict):
                data["_debug"] = {**(extra or {})}
        except Exception:
            # on ne casse jamais la réponse si debug échoue
            pass
        return data

    def _maybe_debug(self, request, data, meta=None):
        if getattr(request.user, "is_authenticated", False):
            user_id = request.user.id
        else:
            user_id = None

        logger.debug({
            "path": request.get_full_path(),
            "method": request.method,
            "user": user_id,
            "meta": meta or {},
            "payload_in_size": len(str(getattr(request, "data", ""))) if hasattr(request, "data") else 0
        })
        if request.query_params.get("debug") == "1" and isinstance(data, dict):
            return self._add_debug(data, extra=meta or {})
        return data


    def finalize_response(self, request, response, *args, **kwargs):
        # Journalisation du statut + taille de sortie
        try:
            out_size = len(str(getattr(response, "data", "")))
        except Exception:
            out_size = None
        logger.debug({"status": response.status_code, "payload_out_size": out_size})
        return super().finalize_response(request, response, *args, **kwargs)


class ArticlePlaygroundViewSet(PlaygroundDebugMixin, ArticleViewSet):
    permission_classes = [AllowAny]
    
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
            return Analysis.objects.none()
        return super().get_queryset()
    
    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        data = getattr(resp, "data", {})
        meta = {"section": "analysis/create"}
        resp.data = self._maybe_debug(request, data, meta)
        return resp

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

