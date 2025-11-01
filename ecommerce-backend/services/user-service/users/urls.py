from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    CurrentUserView,
    UserAddressViewSet,
)

app_name = 'users'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users/me/addresses', UserAddressViewSet, basename='user-address')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('users/me/', CurrentUserView.as_view(), name='current_user'),
    
    # Address endpoints (via router)
    path('', include(router.urls)),
]
