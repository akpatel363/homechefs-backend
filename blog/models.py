from django.db import models
from django.core.validators import MaxValueValidator as Max
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from taggit.managers import TaggableManager

# Create your models here.

type_choices = (
    ('Vegetarian', 'Vegetarian'),
    ('Non-Vegetarian', 'Non-Vegetarian'),
    ('Eggetarian', 'Eggetarian'),
    ('Vegan', 'Vegan')
)


class Recipe(models.Model):
    author = models.ForeignKey(get_user_model(), related_name='recipes', on_delete=models.CASCADE)
    food_type = models.CharField(choices=type_choices, max_length=15, db_index=True)
    image = models.ImageField(blank=True, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    stars = models.DecimalField(decimal_places=1, max_digits=2, default=0)
    servings = models.PositiveSmallIntegerField(validators=[Max(10)])
    cooking_time = models.PositiveSmallIntegerField(null=False, blank=False)
    ingredients = ArrayField(models.CharField(max_length=100))
    steps = ArrayField(models.CharField(max_length=250))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    allow_questions = models.BooleanField(default=True)
    posted = models.BooleanField(default=True)
    tags = TaggableManager()

    def __str__(self):
        return f'Recipe({self.name},{self.author_id})'


class Rating(models.Model):
    by = models.ForeignKey(get_user_model(), related_name='ratings', on_delete=models.CASCADE)
    edited = models.BooleanField(default=False)
    recipe = models.ForeignKey(Recipe, related_name='ratings', on_delete=models.CASCADE)
    stars = models.PositiveSmallIntegerField(validators=[Max(5)])
    body = models.CharField(max_length=200)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['by', 'recipe']

    def __str__(self):
        return f'Rating(recipe={self.recipe_id}, user={self.by_id}, rating={self.stars})'


class Question(models.Model):
    by = models.ForeignKey(get_user_model(), related_name='questions', on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, related_name='questions', on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Question({self.id})'


class Answer(models.Model):
    question = models.OneToOneField(Question, related_name="answer", on_delete=models.CASCADE)
    response = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Answer({self.id},{self.question_id})'
