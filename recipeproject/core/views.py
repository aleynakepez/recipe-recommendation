from django.shortcuts import render, get_object_or_404
from .models import Recipe, RecipeIngredient, Ingredient, IngredientAlternative
from .serializers import RecipeSerializer, RecipeIngredientSerializer, IngredientSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
import os, pickle
from sklearn.metrics.pairwise import cosine_similarity

# CSV_PATH tamamen kaldırıldı!

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Model dosyasını yükle
with open(os.path.join(BASE_DIR, "core", "ml", "ml_models", "recipe_model.pkl"), "rb") as f:
    model_data = pickle.load(f)

df = model_data["df"]
title_vectorizer = model_data["title_vectorizer"]
title_matrix = model_data["title_matrix"]
ingredient_vectorizer = model_data["ingredient_vectorizer"]
ingredient_matrix = model_data["ingredient_matrix"]

# ML tavsiye fonksiyonu
def recommend(query_title, user_ingredients, alpha=0.5, top_n=5):
    title_vec = title_vectorizer.transform([query_title])
    title_scores = cosine_similarity(title_vec, title_matrix).flatten()

    common_ing = set(user_ingredients).intersection(set(ingredient_vectorizer.get_feature_names_out()))
    if not common_ing:
        return []

    ing_text = " ".join(common_ing)
    ing_vec = ingredient_vectorizer.transform([ing_text])
    ing_scores = cosine_similarity(ing_vec, ingredient_matrix).flatten()

    combined = alpha * title_scores + (1 - alpha) * ing_scores
    indices = combined.argsort()[-top_n:][::-1]

    results = []
    for idx in indices:
        results.append({
            "title": df.iloc[idx]["title"],
            "ingredients": df.iloc[idx]["ingredients"],
            "score": round(combined[idx], 3)
        })
    return results


class RecipePagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class RecipeDetailAPIView(APIView):
    def get(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        serializer = RecipeSerializer(recipe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        recipe_id = recipe.id
        recipe.delete()
        return Response({'message': f"Recipe id: {recipe_id} has been deleted successfully."},
                        status=status.HTTP_204_NO_CONTENT)


class GetIngredientsView(APIView):
    def get(self, request):
        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = IngredientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Ingredient Created..'}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FilteredRecipeListAPIView(generics.ListAPIView):
    queryset = Recipe.objects.all().order_by('-created_at')
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['diet_type', 'meal_type', 'season']
    search_fields = ['title']

    def get_serializer_context(self):
        return {'request': self.request}


class MLRecipeRecommendationAPIView(APIView):
    def post(self, request):
        query_title = request.data.get("title", "").strip()
        user_ingredients = [i.strip().lower() for i in request.data.get("ingredients", [])]
        alpha = float(request.data.get("alpha", 0.5))

        if not query_title and not user_ingredients:
            return Response({"error": "At least title or ingredients are required."}, status=400)

        results = []

        exact_match = None
        if query_title:
            exact_match = Recipe.objects.filter(title__icontains=query_title).first()
            if exact_match:
                recipe_ings = [ri.ingredient.name.lower() for ri in exact_match.ingredients.all()]
                missing = list(set(recipe_ings) - set(user_ingredients))
                exact_score = 1.0 if not missing else round(1.0 - len(missing) / len(recipe_ings), 3)

                results.append({
                    "id": exact_match.id,
                    "title": exact_match.title,
                    "ingredients": ", ".join(recipe_ings),
                    "missing_ingredients": ", ".join(missing),
                    "image": request.build_absolute_uri(exact_match.image.url) if exact_match.image else None,
                    "score": exact_score
                })

        adjusted_alpha = alpha if query_title else 0.0
        ml_results = recommend(query_title, user_ingredients, alpha=adjusted_alpha)

        for r in ml_results:
            if not any(r["title"].lower() == x["title"].lower() for x in results):
                matched = Recipe.objects.filter(title__iexact=r["title"]).first()
                recipe_ings = r["ingredients"].split(", ")
                missing = list(set([i.lower() for i in recipe_ings]) - set(user_ingredients))
                results.append({
                    "id": matched.id if matched else None,
                    "title": r["title"],
                    "ingredients": r["ingredients"],
                    "missing_ingredients": ", ".join(missing),
                    "image": request.build_absolute_uri(matched.image.url) if matched and matched.image else None,
                    "score": round(r["score"], 3)
                })

        return Response({"recommendations": results})
