from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from .serializers import TagSerializer, IngredientSerializer,\
                         RecipeSerializer, RecipeDetailSerializer


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


class RecipeViewSet(viewsets.ModelViewSet):
    """ manage recipe objects"""
    permission_classes = (IsAuthenticated, )
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """ retrieve the objects of authenticated user."""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """ return appropriate serializer class."""
        if self.action == 'retrieve':
            return RecipeDetailSerializer

        return self.serializer_class
