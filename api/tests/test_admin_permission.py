# api/tests/test_admin_permission.py
import pytest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from users.permissions import IsAdminUserCustom
from django.contrib.auth import get_user_model

User = get_user_model()


# --- vue fictive protégée ----------
class AdminPingAPIView(APIView):
    permission_classes = [IsAdminUserCustom]

    def get(self, request):
        return Response({"pong": True})


factory = APIRequestFactory()


@pytest.fixture
def normal_user(db):
    return User.objects.create_user(
        username="normal",
        email="normal@example.com",
        password="Pass123!"
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="adminu",
        email="admin@example.com",
        password="Pass123!",
        is_admin=True,          # ← flag custom
    )


@pytest.mark.django_db
def test_admin_permission_denied_for_normal_user(normal_user):
    request = factory.get("/admin-ping/")
    force_authenticate(request, user=normal_user)     # simule user connecté
    response = AdminPingAPIView.as_view()(request)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_permission_granted_for_admin_user(admin_user):
    request = factory.get("/admin-ping/")
    force_authenticate(request, user=admin_user)      # simule admin connecté
    response = AdminPingAPIView.as_view()(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"pong": True}
