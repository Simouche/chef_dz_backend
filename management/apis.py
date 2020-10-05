from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from management.models import TermsAndConditions


class TermsAndConditionsApi(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        queryset = TermsAndConditions.objects.all().values('terms').first()
        return Response(data=queryset)
