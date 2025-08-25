from rest_framework import viewsets, status
import sys
from ..models import SocietyType
from ..serializers import SocietyTypeSerializer

class SocietyTypeViewSet(viewsets.ModelViewSet):
    queryset = SocietyType.objects.all()
    serializer_class = SocietyTypeSerializer
    authentication_classes = ()
    permission_classes = ()