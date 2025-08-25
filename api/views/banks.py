from rest_framework import viewsets, status
import sys
from ..models import Banks
from ..serializers import BankSerializer

class BanksViewSet(viewsets.ModelViewSet):
    queryset = Banks.objects.all()
    serializer_class = BankSerializer
    authentication_classes = ()
    permission_classes = ()