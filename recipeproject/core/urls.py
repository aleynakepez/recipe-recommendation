from django.urls import path
from .views import (RecipeDetailAPIView,
                    GetIngredientsView,
                    FilteredRecipeListAPIView, MLRecipeRecommendationAPIView)

urlpatterns = [
    path('<int:id>/', RecipeDetailAPIView.as_view(), name='recipe-detail'),
    path('ingredients/', GetIngredientsView.as_view(), name='ingredients-list'),
    path('recipes/', FilteredRecipeListAPIView.as_view(), name='recipes-list'),
    path("ml-recommend/", MLRecipeRecommendationAPIView.as_view(), name="ml-recommend"),
]