from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Tag, Ingredient, Recipe

from .serializers import TagSerializer, IngredientSerializer,\
                         RecipeSerializer, RecipeDetailSerializer,\
                         RecipeImageSerializer


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
        elif self.action == 'upload_image':
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ create a new recipe."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """ upload an image to a recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
