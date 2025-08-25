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
from ..models import Menu, Departments, Cities, \
    Stores, Products, Categories, Images, LocationClient, SubCategories, TypeIdentification, Invoice, InvoiceDetail, TransactionData
from ..serializers import UserSerializer, GroupSerializer, \
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



class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    authentication_classes = ()
    permission_classes = ()


class CategoriesStoreViewSet(viewsets.ViewSet):
    serializer_class = ProductsSerializer
    authentication_classes = ()
    permission_classes = ()

    def list(self, request):

        id_store = self.request.query_params.get('id_store', None)

        data = []
        cursor = connection.cursor()
        sql_string_categories = 'select * from api_v_categories_by_store where store_id = ' + str(
            id_store)
        cursor.execute(sql_string_categories)
        columns = [col[0] for col in cursor.description]
        categories = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor2 = connection.cursor()
        sql_string_categories = 'select * from api_v_subcategories_by_store where store_id = ' + str(
            id_store)
        cursor2.execute(sql_string_categories)
        columns_sub = [col[0] for col in cursor2.description]
        subcategories = [
            dict(zip(columns_sub, row)) for row in cursor2.fetchall()
        ]

        for i in categories:
            category_id = i['id']
            data_sub = []
            for a in subcategories:
                if a['category_id'] == category_id:
                    data_sub.append({
                        'id': a['subcategory_id'],
                        'name_subcategory': a['name_subcategory'],
                        'category': a['category_id']
                    })
            data.append({
                'id': i['id'],
                'name_category': i['name_category'],
                'icon': i['icon'],
                'rel_categories': data_sub
            })
        return Response(data)





class SubCategoriesViewSet(viewsets.ModelViewSet):
    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """http://127.0.0.1:8000/api/subcategories?id_category=1"""
        queryset = SubCategories.objects.all()
        id_category = self.request.query_params.get('id_category', None)
        if id_category is not None:
            queryset = SubCategories.objects.filter(category_id=id_category)
        return queryset


class FindCategoryBySubcategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """http://127.0.0.1:8000/api/subcategories?id_category=1"""
        subcategory_id = self.request.query_params.get('subcategory_id', None)
        if subcategory_id is not None:
            queryset = SubCategories.objects.filter(id=subcategory_id)
        return queryset
