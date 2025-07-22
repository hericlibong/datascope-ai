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
    class Meta:
        model = DatasetSuggestion
        fields = (
            "id",
            "title",
            "description",
            "link",
            "source",
            "found_by",
            "formats",        # 🆕
            "organisation",   # 🆕  orthographe FR / DB
            "licence",        # 🆕
            "last_modified",  # 🆕
            "richness",       # 🆕
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

      
    