from django.urls import path
from .views import (
      LoginView , RegisterView, LogoutView, 
      PasswordChangeView , PasswordResetConfirmView , PasswordResetRequestView,
      AddFavoriteRecipeAPIView, FavoriteListAPIView, ProfileAPIView)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
      path('register/', RegisterView.as_view(), name='register'),
      path('login/', LoginView.as_view(), name='login'),
      path('logout/', LogoutView.as_view(),name='logout'),   #jwt
      path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
      path("password-reset-confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
      path("password-change/", PasswordChangeView.as_view(), name="password-change"),
      path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
      #Access token süresi dolduğunda kullanıcı tekrar login olmak zorunda kalmasın diye token refresh endpoint
      path('favorites/', FavoriteListAPIView.as_view(), name='favorites-list'),
      path('favorites/<int:recipe_id>/add/', AddFavoriteRecipeAPIView.as_view(), name='favorites-add'),
      path('profile/', ProfileAPIView.as_view(), name='user-profile'),
]