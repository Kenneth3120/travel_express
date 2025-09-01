from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsMemberOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'member']


class ReadOnlyForViewer(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 'viewer':
            return request.method in SAFE_METHODS
        return True
