from django.db.models.signals import post_save
from django.db.models import Avg
from django.dispatch import receiver
from .models import Rating


@receiver(post_save, sender=Rating)
def update_recipe_rating(instance, **kwargs):
    recipe = instance.recipe
    recipe.stars = Rating.objects.filter(recipe=recipe).values("stars").aggregate(avg=Avg("stars"))["avg"]
    recipe.save()
