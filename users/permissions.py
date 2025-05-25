# users/permissions.py
from rest_framework import permissions

class IsAdminUserCustom(permissions.BasePermission):
    """Accorde l’accès si request.user.is_admin est True."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)
