from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    TowerInstanceViewSet,
    CredentialViewSet,
    ExecutionEnvironmentViewSet,
    AuditLogViewSet,
    TowerCredentialProxy,
    UserViewSet,
    user_info,
    test_connection,
    credential_type_status,
    duplicate_missing_credential_type,
    verify_credential_type_by_name
)

router = DefaultRouter()

router.register(r'tower-credentials', TowerCredentialProxy, basename='tower-credentials')
router.register(r'tower', TowerInstanceViewSet, basename='tower')
router.register(r'instances', TowerInstanceViewSet, basename='instance')
router.register(r'credentials', CredentialViewSet)
router.register(r'environments', ExecutionEnvironmentViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-info/', user_info),
    path('test-connection/', test_connection),
    path('credential-type-status/', credential_type_status),
    path('duplicate-credential-type/', duplicate_missing_credential_type),
    path('verify-credential-type/', verify_credential_type_by_name),
    path('', include(router.urls)),
]
