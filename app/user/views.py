from rest_framework import generics, permissions

from .serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """ creating a new user."""
    serializer_class = UserSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """ manage authenticated users profile"""
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = UserSerializer

    def get_object(self):
        """ retrieve user object."""
        return self.request.user
