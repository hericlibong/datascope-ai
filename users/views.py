from rest_framework import generics, viewsets, permissions
from .serializers import (
    UserRegistrationSerializer,
    FeedbackSerializer,
)
from .models import Feedback


# ---------- Registration ----------
class UserRegistrationAPIView(generics.CreateAPIView):
    """
    POST /users/register/   -> créer un compte
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


# ---------- Feedback ----------
class FeedbackViewSet(viewsets.ModelViewSet):
    """
    POST /feedbacks/        -> envoyer un feedback
    GET  /feedbacks/        -> lister mes feedbacks
    """
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user).order_by("-submitted_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
