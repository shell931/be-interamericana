from rest_framework import viewsets, status
import sys
from ..models import TypeAccount
from ..serializers import TypeAccountSerializer

class TypeAccountViewSet(viewsets.ModelViewSet):
    queryset = TypeAccount.objects.all()
    serializer_class = TypeAccountSerializer
    authentication_classes = ()
    permission_classes = ()