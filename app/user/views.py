from rest_framework import generics, permissions, authentication

from .serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """ creating a new user."""
    serializer_class = UserSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """ manage authenticated users profile"""
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (authentication.TokenAuthentication, )
    serializer_class = UserSerializer

    def get_object(self):
        """ retrieve user object."""
        return self.request.user
