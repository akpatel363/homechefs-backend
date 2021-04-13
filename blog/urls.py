from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, AuthorViewSet, create_answer

router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('authors', AuthorViewSet)

urlpatterns = router.urls + [
    path('questions/<int:pk>/answer/', create_answer),
]
