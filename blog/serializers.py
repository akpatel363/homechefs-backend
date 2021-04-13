from django.contrib.auth import get_user_model
from django.template.defaultfilters import truncatewords
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField
from rest_framework import serializers
from easy_thumbnails.templatetags.thumbnail import thumbnail_url
from .models import Recipe, Rating, Question, Answer


class ThumbnailField(serializers.ImageField):
    def __init__(self, alias='small', **kwargs):
        self.alias = alias
        super().__init__(**kwargs)

    def to_representation(self, value):
        return None if not value else thumbnail_url(value, self.alias)

    def to_internal_value(self, data):
        if type(data) == list:
            return super().to_internal_value(data[0])
        else:
            return super().to_internal_value(data)


class AuthorSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        full_name = obj.get_full_name()
        return obj.username if not full_name else full_name

    class Meta:
        model = get_user_model()
        fields = ('id', 'name', 'username')
        read_only_fields = ('name', 'username')


class AuthorDetailsSerializer(AuthorSerializer):
    class Meta(AuthorSerializer.Meta):
        fields = AuthorSerializer.Meta.fields + ('date_joined',)


class RecipeSerializerForAuthor(serializers.ModelSerializer):
    stars = serializers.DecimalField(2, decimal_places=1)
    image = ThumbnailField()

    class Meta:
        model = Recipe
        exclude = ('description', 'steps', 'ingredients', 'servings', 'cooking_time')


class SmallRecipeSerializer(TaggitSerializer, serializers.ModelSerializer):
    image = ThumbnailField()
    short_description = serializers.SerializerMethodField()
    tags = TagListSerializerField()

    def get_short_description(self, obj):
        return truncatewords(obj.description, 20)

    class Meta:
        model = Recipe
        exclude = ('steps', 'ingredients', 'description')


class RecipeSerializer(SmallRecipeSerializer):
    author = AuthorSerializer()


class SimilarRecipeSerializer(serializers.ModelSerializer):
    image = ThumbnailField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'stars', 'image')


class RecipeDetailSerializer(TaggitSerializer, serializers.ModelSerializer):
    author = AuthorSerializer(default=serializers.CurrentUserDefault())
    image = ThumbnailField(alias="medium", allow_null=True)
    stars = serializers.DecimalField(read_only=True, decimal_places=1, max_digits=2)
    tags = TagListSerializerField()

    class Meta:
        model = Recipe
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    by = AuthorSerializer(default=serializers.CurrentUserDefault())

    class Meta:
        model = Rating
        exclude = ('recipe',)
        read_only_fields = ('edited',)


class RatingGroup(serializers.Serializer):
    stars = serializers.IntegerField()
    count = serializers.IntegerField()


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('response', 'created', 'question')
        extra_kwargs = {'question': {'read_only': True}}


class QuestionSerializer(serializers.ModelSerializer):
    by = AuthorSerializer(default=serializers.CurrentUserDefault())
    answer = AnswerSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'question', 'answer', 'created', 'by')
