from rest_framework import permissions

class IsStoreOwner(permissions.BasePermission):
    """
    Custom permission to only allow store owners to create/edit products.
    """
    def has_permission(self, request, view):
        # Check if the user is trying to create or edit a product
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return request.user.is_authenticated and request.user.is_store_owner
        # Allow everyone to view products
        return True

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow authenticated users to read-only access.
    """
    def has_permission(self, request, view):
        # Allow read-only access for any request
        if view.action in ['list', 'retrieve']:
            return True
        # Allow only authenticated users for any other actions
        return request.user.is_authenticated