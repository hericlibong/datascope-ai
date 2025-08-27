# analysis/serializers.py
from rest_framework import serializers
from .models import (
    Article,
    Analysis,
    Entity,
    Angle,
    VisualizationSuggestion,
    DatasetSuggestion,
)


# ---------- leaf serializers ----------
class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ("id", "type", "value", "context")


class VisualizationSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisualizationSuggestion
        fields = ("id", "chart_type", "description", "markdown_snippet")


class AngleSerializer(serializers.ModelSerializer):
    visualizations = VisualizationSuggestionSerializer(many=True, read_only=True)

    class Meta:
        model = Angle
        fields = ("id", "title", "description", "order", "visualizations")


class DatasetSuggestionSerializer(serializers.ModelSerializer):
    # --- NEW: always expose a unified 'link' and 'source' for the UI
    link = serializers.SerializerMethodField()    # NEW (unified output)
    source = serializers.SerializerMethodField()  # NEW (unified output)

    # --- NEW: expose validation if present (runtime on Pydantic objects)
    validation = serializers.SerializerMethodField(required=False)

    def get_link(self, obj):  # NEW (unified output)
        """
        Prefer source_url (Pydantic/connector objects), fallback to DB 'link'.
        This keeps a stable 'link' key for the UI in all cases.
        """
        # dict support (angle_resources path)
        if isinstance(obj, dict):
            return obj.get("source_url") or obj.get("link")
        # object support
        return getattr(obj, "source_url", None) or getattr(obj, "link", None)

    def get_source(self, obj):  # NEW (unified output)
        """
        Prefer source_name (Pydantic/connector objects), fallback to DB 'source'.
        """
        if isinstance(obj, dict):
            return obj.get("source_name") or obj.get("source")
        return getattr(obj, "source_name", None) or getattr(obj, "source", None)

    def get_validation(self, obj):
        # obj may be a dict or a model/Pydantic object
        if isinstance(obj, dict):
            return obj.get("validation")
        return getattr(obj, "validation", None)

    class Meta:
        model = DatasetSuggestion
        fields = (
            "id",
            "title",
            "description",
            # historical DB fields:
            "link",            # unified alias (SerializerMethodField)
            "source",          # unified alias (SerializerMethodField)
            "found_by",
            "formats",
            "organisation",
            "licence",
            "last_modified",
            "richness",
            "validation",      # runtime-only field from pipeline (if present)
        )


# ---------- article & analysis ----------
class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Article
        fields = (
            "id",
            "user",
            "title",
            "content",
            "file",
            "language",
            "submitted_at",
        )
        read_only_fields = ("title", "submitted_at")

    # règle métier : au moins 200 mots
    def validate_content(self, value):
        if value and len(value.split()) < 200:
            raise serializers.ValidationError("Article must contain at least 200 words.")
        return value

    def create(self, validated_data):
        # titre auto : 10 premiers mots
        content = validated_data.get("content", "")
        if content:
            validated_data["title"] = " ".join(content.split()[:10])
        return super().create(validated_data)


class AnalysisSerializer(serializers.ModelSerializer):
    angle_resources = serializers.JSONField(read_only=True)
    article = ArticleSerializer(read_only=True)

    class Meta:
        model = Analysis
        fields = ("id", "article", "score", "profile_label", "summary", "created_at", "angle_resources")
        read_only_fields = ("created_at",)


# ---------- analysis detail (nested) ----------
class AnalysisDetailSerializer(AnalysisSerializer):
    entities = EntitySerializer(many=True, read_only=True)
    angles = AngleSerializer(many=True, read_only=True)
    datasets = DatasetSuggestionSerializer(many=True, read_only=True)

    class Meta(AnalysisSerializer.Meta):
        fields = AnalysisSerializer.Meta.fields + ("entities", "angles", "datasets")


# ---------- ressources par angle (backend v2) ----------
# 1) suggestions de portails / bases (LLM)
class LLMSuggestionSerializer(serializers.Serializer):
    title       = serializers.CharField()
    description = serializers.CharField()
    link        = serializers.URLField()
    source      = serializers.CharField()

    # --- NEW: mirrors for historical keys expected by some UIs
    source_url  = serializers.SerializerMethodField()        # NEW (unified output)
    source_name = serializers.SerializerMethodField()        # NEW (unified output)

    # --- NEW: expose validation if present (annotated by pipeline)
    validation  = serializers.SerializerMethodField(required=False)

    def get_source_url(self, obj):  # NEW (unified output)
        if isinstance(obj, dict):
            return obj.get("link")
        return getattr(obj, "link", None)

    def get_source_name(self, obj):  # NEW (unified output)
        if isinstance(obj, dict):
            return obj.get("source")
        return getattr(obj, "source", None)

    def get_validation(self, obj):
        if isinstance(obj, dict):
            return obj.get("validation")
        return getattr(obj, "validation", None)


# 2) suggestions de visus (LLM)
class VizSuggestionSerializer(serializers.Serializer):
    title       = serializers.CharField()
    chart_type  = serializers.CharField()
    x           = serializers.CharField()
    y           = serializers.CharField()
    note        = serializers.CharField(allow_null=True, required=False)


# 3) agrégateur final : tout ce qui concerne UN angle
class AngleResourcesSerializer(serializers.Serializer):
    index          = serializers.IntegerField()
    title          = serializers.CharField()
    description    = serializers.CharField()
    keywords       = serializers.ListField(child=serializers.CharField())
    datasets       = DatasetSuggestionSerializer(many=True)
    sources        = LLMSuggestionSerializer(many=True)
    visualizations = VizSuggestionSerializer(many=True)
