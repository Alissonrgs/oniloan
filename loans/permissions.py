# third party
from rest_framework.permissions import BasePermission


class LoanPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return view.loan.client == request.user
