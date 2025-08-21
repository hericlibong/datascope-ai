from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_playground import (
    ArticlePlaygroundViewSet,
    AnalysisPlaygroundViewSet,
    FeedbackPlaygroundViewSet,
    HistoryPlaygroundAPIView,
)

router = DefaultRouter()
router.register(r"articles", ArticlePlaygroundViewSet, basename="play-article")
router.register(r"analysis", AnalysisPlaygroundViewSet, basename="play-analysis")
router.register(r"feedbacks", FeedbackPlaygroundViewSet, basename="play-feedback")

urlpatterns = [
    path("history/", HistoryPlaygroundAPIView.as_view(), name="play-analysis-history"),
    path("", include(router.urls)),
]
