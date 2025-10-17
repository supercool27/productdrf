from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.authtoken.views import obtain_auth_token

from .views import ProductViewSet, OrderViewSet


router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet, basename="order")


urlpatterns = [
    path("v1/auth/jwt/create/", TokenObtainPairView.as_view(), name="jwt_obtain_pair"),
    path("v1/auth/jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh"),
    path("v1/auth/token/", obtain_auth_token, name="api_token_auth"),
    path("v1/", include(router.urls)),
]


