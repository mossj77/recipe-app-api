from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient

from .serializers import TagSerializer, IngredientSerializer


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """ base class to make recipe attributes easier."""
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """ retrieve object of authenticated user."""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """ create new objects. """
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """ manage Tag in database. """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """ manage Ingredient in database. """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
