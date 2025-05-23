from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """
    Custom User for DataScope AI
    - Login: username + password (Django standard scheme)
    - Email is required and unique
    - is_admin field for future permissions
    """
    email = models.EmailField(unique=True, blank=False)
    is_admin = models.BooleanField(default=False)

    # Keep authentication by username
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"


class UserProfile(models.Model):
    """
    Extended profile (optional).
    Automatically created when a User is created; all fields are optional.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    bio = models.TextField(blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"
    

class Feedback(models.Model):
    """Feedback utilisateur (général ou lié à une analyse)."""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedbacks",
    )
    analysis = models.ForeignKey(
        "analysis.Analysis",          # référence chaîne pour éviter l’import circulaire
        on_delete=models.CASCADE,
        related_name="feedbacks",
        blank=True,
        null=True,
    )

    relevance   = models.IntegerField(choices=RATING_CHOICES, blank=True, null=True)
    angles      = models.IntegerField(choices=RATING_CHOICES, blank=True, null=True)
    sources     = models.IntegerField(choices=RATING_CHOICES, blank=True, null=True)
    reusability = models.IntegerField(choices=RATING_CHOICES, blank=True, null=True)

    message       = models.TextField(blank=True)
    submitted_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-submitted_at",)

    def __str__(self):
        if self.analysis:
            return f"Feedback by {self.user.username} on analysis #{self.analysis_id}"
        return f"General feedback by {self.user.username}"


# --------------------------------------------------------------------
# Signal: create or update the profile each time a User is saved
# --------------------------------------------------------------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # If the profile already exists, ensure it is saved
        instance.profile.save()
