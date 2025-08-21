from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from analysis.views import ArticleViewSet, AnalysisViewSet, HistoryAPIView
from users.views import FeedbackViewSet, UserRegistrationAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r"articles", ArticleViewSet, basename="article")
router.register(r"analysis", AnalysisViewSet, basename="analysis")
router.register(r"feedbacks", FeedbackViewSet, basename="feedback")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/register/", UserRegistrationAPIView.as_view(), name="user-register"),
    path("history/", HistoryAPIView.as_view(), name="analysis-history"),
    path("", include(router.urls)),
]

# --- Playground namespace (uniquement si activé)
if getattr(settings, "PLAYGROUND_DEBUG_MODE", False):
    urlpatterns += [
        path("playground/", include("api.playground_urls")),
    ]

