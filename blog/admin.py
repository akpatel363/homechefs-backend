from django.contrib import admin
from .models import Recipe, Rating, Question, Answer


# Register your models here.


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('created', 'food_type')
    raw_id_fields = ('author',)
    exclude = ('slug',)
    list_per_page = 20


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'updated', 'edited')
    raw_id_fields = ('by', 'recipe')
    list_per_page = 20


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'question', 'created')
    raw_id_fields = ('recipe', 'by')
    list_filter = ('recipe',)
    list_per_page = 20


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'response', 'created')
    raw_id_fields = ('question',)
    list_per_page = 20
