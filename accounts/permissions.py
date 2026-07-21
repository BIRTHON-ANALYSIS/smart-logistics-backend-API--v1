
from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    """
    Base permission that checks whether
    the authenticated user's role is allowed.
    """

    allowed_roles = []

    def has_permission(self, request, view):

        print("Username:", request.user.username)
        print("Role:", repr(request.user.role))
        print("Allowed:", self.allowed_roles)

        return (
            request.user.is_authenticated and
            request.user.role in self.allowed_roles
        )


class IsAdmin(HasRole):
    allowed_roles = ["admin"]


class IsDispatcher(HasRole):
    allowed_roles = ["dispatcher"]


class IsCustomer(HasRole):
    allowed_roles = ["customer"]


class IsDriver(HasRole):
    allowed_roles = ["driver"]


class IsAdminOrDispatcher(HasRole):
    allowed_roles = ["admin", "dispatcher"]

    