from rest_framework import permissions
from organizations import models as organizations_models


# IF USER IS AN ORG
class IsOrganization(permissions.BasePermission):
    message = "Only organizations are allowed"

    def has_permission(self, request, view):
        organizations = organizations_models.Organization.objects.filter(user=request.user)
        if len(organizations):
            return True
        return False

