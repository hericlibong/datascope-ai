import pytest
from django.contrib.auth import get_user_model
from users.models import UserProfile

User = get_user_model()


@pytest.mark.django_db
def test_user_str_and_profile_created():
    """
    - Lorsqu'on crée un utilisateur, le signal doit générer un UserProfile.
    - La méthode __str__ doit retourner "username (email)".
    """
    user = User.objects.create_user(
        username="alice",
        email="alice@example.com",
        password="S@cret123",
    )

    # Vérifie la chaîne de représentation
    assert str(user) == "alice (alice@example.com)"

    # Vérifie que le profil lié existe automatiquement
    profile = UserProfile.objects.get(user=user)
    assert profile is not None
    assert profile.user == user
