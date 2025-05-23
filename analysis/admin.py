from django.contrib import admin
from .models import Article, Analysis, Entity, Angle, VisualizationSuggestion, DatasetSuggestion

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "language", "submitted_at")
    list_filter  = ("language", "submitted_at")
    search_fields = ("title", "user__username", "user__email")

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "article", "score", "profile_label", "created_at")
    list_filter  = ("profile_label",)
    search_fields = ("article__title", "article__user__username")
    date_hierarchy = "created_at"

admin.site.register(Entity)
admin.site.register(Angle)
admin.site.register(VisualizationSuggestion)
admin.site.register(DatasetSuggestion)