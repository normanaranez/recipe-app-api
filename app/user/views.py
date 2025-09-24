"""
Views for the user API View.
"""

from rest_framework import generics, authentication, permissions

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer