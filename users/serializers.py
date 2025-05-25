# users/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, Feedback


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("bio", "organization", "job_title", "website")


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "is_admin", "profile")


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class FeedbackSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "user",
            "analysis",
            "relevance",
            "angles",
            "sources",
            "reusability",
            "message",
            "submitted_at",
        )
        read_only_fields = ("submitted_at",)

    # ------- validation renforcée -------
    def validate(self, attrs):
        ratings = [
            attrs.get("relevance"),
            attrs.get("angles"),
            attrs.get("sources"),
            attrs.get("reusability"),
        ]

        # Si au moins une note est renseignée…
        if any(r is not None for r in ratings):
            # … exige qu’elles le soient toutes
            if not all(r is not None for r in ratings):
                raise serializers.ValidationError(
                    "Provide all four ratings (relevance, angles, sources, reusability) or none."
                )
        # Sinon, s’il n’y a aucune note, on exige au moins un message
        elif not attrs.get("message"):
            raise serializers.ValidationError(
                "Submit either a message or the full set of ratings."
            )

        return attrs
