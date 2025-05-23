# analysis/models.py
from django.db import models
from django.conf import settings


def article_upload_to(instance, filename):
    """Stores uploaded files in media/articles/<userid>/<filename>"""
    return f"articles/{instance.user.id}/{filename}"

# -------------------------------------------------------------------
# 1) Article
# -------------------------------------------------------------------
class Article(models.Model):
    """Text or file submitted for analysis."""
    LANGUAGE_CHOICES = [
        ("fr", "Français"),
        ("en", "English"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
    )
    title = models.CharField(max_length=255, blank=True, editable=False)
    content = models.TextField(blank=True)                # raw text (copy-paste or excerpt)
    file = models.FileField(upload_to=article_upload_to, blank=True, null=True)
    language = models.CharField(max_length=2, 
                                choices=LANGUAGE_CHOICES,
                                help_text="Language chosen by the user (used for the interface and prompts)")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-submitted_at",)

    def __str__(self) -> str:
        return f"{self.title or 'Untitled'} – {self.user.username}"
    

# -------------------------------------------------------------------
# 2) Analysis
# -------------------------------------------------------------------
class Analysis(models.Model):
    """Aggregated AI result for a given article."""

    article = models.OneToOneField(
        Article,
        on_delete=models.CASCADE,
        related_name="analysis",
        help_text="The article this analysis refers to"
    )
    score = models.FloatField(
    help_text="Datafication score (0–10) indicating the density of structured data"
    )
    profile_label = models.CharField(
        max_length=50,
        help_text="Short label describing the data profile (e.g. 'Low potential', 'High potential')"
    )
    summary = models.TextField(
        blank=True,
        null=True,
        help_text="Optional AI-generated summary of the article content"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the analysis was generated"
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Analysis of Article #{self.article_id}"
    
# -------------------------------------------------------------------
# 3) Entity
# -------------------------------------------------------------------
class Entity(models.Model):
    """Single extracted entity (named entity, number, date, etc.)."""
    ENTITY_TYPES = [
        ("PER", "Person"),
        ("ORG", "Organization"),
        ("LOC", "Location"),
        ("DATE", "Date"),
        ("NUM", "Number"),
        ("MISC", "Misc"),
    ]

    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.CASCADE,
        related_name="entities",
        help_text="The analysis that produced this entity"
    )
    type = models.CharField(max_length=4, choices=ENTITY_TYPES)
    value = models.CharField(max_length=255)
    context = models.TextField(blank=True, null=True, help_text="Sentence excerpt")

    def __str__(self):
        return f"{self.get_type_display()}: {self.value}"
    
# -------------------------------------------------------------------
# 4) Angle
# -------------------------------------------------------------------
class Angle(models.Model):
    """Editorial angle suggested by the AI."""
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.CASCADE,
        related_name="angles",
        help_text="Analysis from which this angle was generated"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0, help_text="Display order")

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return self.title

# -------------------------------------------------------------------
# 5) VisualizationSuggestion
# -------------------------------------------------------------------
class VisualizationSuggestion(models.Model):
    """Suggested chart or visual linked to an angle."""
    
    angle = models.ForeignKey(
        Angle,
        on_delete=models.CASCADE,
        related_name="visualizations"
    )
    chart_type = models.CharField(max_length=30)
    description = models.TextField()
    markdown_snippet = models.TextField(
        blank=True, null=True,
        help_text="Optional pre-formatted markdown for the front-end"
    )

    def __str__(self):
        return f"{self.chart_type} for '{self.angle.title}'"

# -------------------------------------------------------------------
# 6) DatasetSuggestion
# -------------------------------------------------------------------
class DatasetSuggestion(models.Model):
    """Open dataset recommended for further investigation."""
    SOURCE_TYPES = [
        ("LLM", "Generated by LLM"),
        ("CONNECTOR", "Found via API connector"),
    ]

    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.CASCADE,
        related_name="datasets"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField()
    source = models.CharField(max_length=20)
    found_by = models.CharField(max_length=10, choices=SOURCE_TYPES)

    def __str__(self):
        return self.title
