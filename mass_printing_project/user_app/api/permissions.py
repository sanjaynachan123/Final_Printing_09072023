from rest_framework import permissions


class IsAdminOrUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        is_admin = bool(request.user and request.user.is_staff)
        is_himself = obj.uploader == request.user
        return is_admin or is_himself