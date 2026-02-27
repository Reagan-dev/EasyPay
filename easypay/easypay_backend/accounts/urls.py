from django.urls import path
from .views import (
    RegisterView, 
    LoginView, 
    LogoutView, 
    UserProfileView, 
    CustomTokenRefreshView
)

urlpatterns = [
    # Auth Endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Token Management
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # User Info
    path('me/', UserProfileView.as_view(), name='user_profile'),
]