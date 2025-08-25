from django.db.models import query
from rest_framework import viewsets, status
import sys
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
import hashlib
import math
import time
from ..models import Binnacle, Menu, Departments, Cities, \
    Stores, Products, Categories, Images, LocationClient, SubCategories, TypeIdentification, Invoice, InvoiceDetail, TransactionData
from ..serializers import GetBinnaclesSerializer, UserSerializer, GroupSerializer, \
    MenuSerializer, CreateUserSerializer, StoresSerializer, \
    DepartmentsSerializer, CitiesSerializer, ProductsSerializer,\
    CategoriesSerializer, ImagesSerializer, ProductsFrontStoreSerializer, \
    AdminProductSerializer, LocationClientSerializer, LocationClientByUserSerializer, SubCategoriesSerializer, TypeIdentificationSerializer, InvoiceDetalSerializer, InvoiceSerializer
from django.contrib.auth.models import Group
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from itertools import chain
from django.db import connection
import json
import collections
import requests
from datetime import date
from datetime import datetime
from django.db.models import Sum, Count
from django.http import JsonResponse

class BinnaclesCheckReturnViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        # id_invoice = int(self.request.query_params.get('id_invoice', None))
        data = []
        binnacle_model = Binnacle.objects.all().filter(check_binnacle = False).order_by('id_invoice_id').distinct('id_invoice_id')
        for item  in binnacle_model:
            number_invoice = Binnacle.objects.filter(id_invoice_id = item.id_invoice_id).count()
            id_inv = str(item.id_invoice)
            id_invoice = item.id_invoice_id
            data.append({
                'id_inv': id_inv,
                'id_invoice': item.id_invoice_id,
                'number_invoice': number_invoice
            })
        return Response(data)