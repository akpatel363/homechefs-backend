from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.author_id == request.user.id:
            return True
        if request.method in SAFE_METHODS and obj.posted:
            return True
        return False
