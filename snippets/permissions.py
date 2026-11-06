
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow anyone to view snippets.
    Only the owner can edit or delete a snippet.
    """

    def has_object_permission(self, request, view, obj):
        # Read-only requests are allowed for everyone.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only the owner can make changes.
        return obj.owner == request.user
