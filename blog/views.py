from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.generics import RetrieveAPIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Recipe, Rating, Question
from .pagination import Pagination
from .filters import RecipeFilter
from .parsers import RecipeMultiPartParser
from . import permissions
from . import serializers


# Create your views here.

class RecipeViewSet(ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, permissions.IsAuthorOrReadOnly)
    parser_classes = (JSONParser, FormParser, RecipeMultiPartParser)
    serializer_class = serializers.RecipeSerializer
    filterset_class = RecipeFilter
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('stars', 'cooking_time', 'servings', 'created')
    search_fields = ('name',)
    ordering = ('-created',)
    queryset = Recipe.objects.prefetch_related('tags').select_related('author')

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        rating_groups = self.get_rating_groups(obj.id)
        return Response({'recipe': serializer.data, 'rating_groups': rating_groups.data})

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(posted=True).defer('ingredients', 'steps') if self.action == 'list' else queryset

    def get_serializer_class(self):
        return serializers.RecipeSerializer if self.action == 'list' else serializers.RecipeDetailSerializer

    def get_rating_groups(self, id):
        rating_groups = Rating \
            .objects \
            .filter(recipe_id=id) \
            .values('stars') \
            .annotate(count=Count('id'))
        serializer = serializers.RatingGroup(rating_groups, many=True)
        return serializer

    @action(detail=False, permission_classes=[IsAuthenticated], methods=['GET'])
    def my(self, request):
        recipes = Recipe \
            .objects \
            .filter(author=request.user) \
            .defer('ingredients', 'steps', 'description', 'cooking_time', 'servings') \
            .order_by('-created')
        serializer = serializers.RecipeSerializerForAuthor(recipes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def ratings(self, request, pk):
        ratings = Rating.objects.filter(recipe_id=pk).select_related('by').order_by('-updated')
        paginator = Pagination()
        result = paginator.paginate_queryset(ratings, request)
        serializer = serializers.RatingSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, url_path='ratings/my', methods=['GET', 'POST'], permission_classes=[IsAuthenticated])
    def my_rating(self, request, pk):
        if request.method == 'POST':
            rating = Rating.objects.filter(recipe_id=pk, by=request.user).first()
            serializer = serializers.RatingSerializer(rating, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            if rating:
                serializer.save(edited=True)
            else:
                recipe = get_object_or_404(Recipe, id=pk, posted=True)
                serializer.save(recipe=recipe)
            return Response(serializer.data)
        else:
            rating = Rating.objects.filter(recipe_id=pk, by=request.user).select_related('by').first()
            if not rating:
                return Response()
            serializer = serializers.RatingSerializer(rating)
            return Response(serializer.data)

    @action(detail=True, methods=['GET', 'POST'], permission_classes=[IsAuthenticatedOrReadOnly])
    def questions(self, request, pk):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk, posted=True, allow_questions=True)
            if recipe.author == request.user:
                return Response({'detail': 'You cannot ask yourself a question.'}, status.HTTP_403_FORBIDDEN)
            serializer = serializers.QuestionSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe)
            return Response(serializer.data)
        else:
            questions = Question.objects.filter(recipe_id=pk).select_related('by', 'answer').order_by('-created')
            if 'search' in request.query_params:
                search = request.query_params['search']
                questions = questions.filter(Q(question__icontains=search) | Q(answer__response__icontains=search))
            paginator = Pagination()
            result = paginator.paginate_queryset(questions, request)
            serializer = serializers.QuestionSerializer(result, many=True)
            return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['GET'])
    def similar(self, req, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        query = Recipe \
                    .objects \
                    .filter(tags__in=recipe.tags.values_list('id', flat=True)) \
                    .exclude(id=recipe.id) \
                    .only('name', 'image', 'stars') \
                    .annotate(similar_tags=Count('tags')) \
                    .order_by('-similar_tags', '-stars')[0:4]
        serializer = serializers.SimilarRecipeSerializer(query, many=True)
        return Response(serializer.data)


class AuthorViewSet(GenericViewSet, RetrieveAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.AuthorDetailsSerializer

    @action(detail=True, methods=['GET'])
    def recipes(self, request, pk):
        queryset = Recipe.objects.filter(author_id=pk, posted=True).prefetch_related('tags')
        pagination = Pagination()
        results = pagination.paginate_queryset(queryset, request)
        serializer = serializers.SmallRecipeSerializer(results, many=True)
        return pagination.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_answer(req, pk):
    question = get_object_or_404(Question, pk=pk, recipe__author=req.user)
    serializer = serializers.AnswerSerializer(data=req.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(question=question)
    return Response(serializer.data)
