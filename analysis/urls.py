from django.urls import path
from .views import ArticleAnalyzeAPIView


urlpatterns = [
    path("", ArticleAnalyzeAPIView.as_view(), name="article-analyze"),
]