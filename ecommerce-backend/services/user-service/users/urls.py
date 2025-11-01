from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    CurrentUserView,
    UserAddressViewSet,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangePasswordView,
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
    
    # Password management endpoints
    path('auth/password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # User profile endpoints
    path('users/me/', CurrentUserView.as_view(), name='current_user'),
    
    # Address endpoints (via router)
    path('', include(router.urls)),
]
