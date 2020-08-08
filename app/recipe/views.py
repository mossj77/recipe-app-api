from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import Tag

from .serializers import TagSerializer


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """ manage Tag in database. """
    permission_classes = (IsAuthenticated, )
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self):
        """ retrieve tags of authenticated user."""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
