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

from ..serializers import *

from django.contrib.auth.models import Group
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from itertools import chain
from django.db import connection
import json
import collections
import requests


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken,
                         self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user_info = User.objects.get(id=token.user_id)
        store_id = user_info.store_id
        if (user_info.type_user_id == 3):
            response = {
                'token': token.key,
                'user_id': token.user_id,
                'id_store': store_id,
                'type_user': user_info.type_user_id,
                'personal_name': user_info.first_name+' '+user_info.last_name,
                'user_email': user_info.email
            }
        else:
            response = {
                'token': token.key,
                'user_id': token.user_id,
                'id_store': store_id,
                'type_user': user_info.type_user_id,
                'personal_name': user_info.first_name+' '+user_info.last_name,
                'user_email': user_info.email
            }
        return Response(response, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    @action(detail=True, methods=['PUT', 'DELETE'])
    def action_user(self, request, pk=None):
        if request.method == 'PUT':
            try:
                first_name = request.data['first_name']
                last_name = request.data['last_name']
                product = User.objects.get(id=pk)
                product.first_name = first_name
                product.last_name = last_name
                product.save()
                response = {'message': 'User update correctly', 'result': 200}
                return Response(response, status=status.HTTP_200_OK)
            except:
                response = {'message': 'No put user', 'result': 400}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)


class CreateUserViewSet(viewsets.ViewSet):
    serializer_class = CreateUserSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def create(self, request):
        serializer = CreateUserSerializer
        return Response(serializer)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        id_user = self.request.user.id
        object_user_group = User.groups.through.objects.get(user_id=id_user)
        group_id = object_user_group.group_id
        queryset = Group.objects.filter(id=group_id)
        return queryset


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        id_user = self.request.user.id
        object_user_group = User.groups.through.objects.get(user_id=id_user)
        group_id = object_user_group.group_id
        object_group_menu = Group.menu.through.objects.filter(
            group_id=group_id)
        list_menu = []
        for e in object_group_menu:
            list_menu.append(e.menu_id)

        queryset = Menu.objects.filter(id_menu__in=list_menu)
        return queryset


class GroupListViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )


class DepartmentsViewSet(viewsets.ModelViewSet):
    queryset = Departments.objects.all()
    serializer_class = DepartmentsSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )


class DepartmentsFrontViewSet(viewsets.ModelViewSet):
    queryset = Departments.objects.all()
    serializer_class = DepartmentsSerializer
    authentication_classes = ()
    permission_classes = ()


class TypeIdentifiersFrontViewSet(viewsets.ModelViewSet):
    queryset = TypeIdentification.objects.all()
    serializer_class = TypeIdentificationSerializer
    authentication_classes = ()
    permission_classes = ()


class CitiesViewSet(viewsets.ModelViewSet):
    queryset = Cities.objects.all()
    serializer_class = CitiesSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """http://127.0.0.1:8000/api/cities?id_departament=5"""
        queryset = Cities.objects.all()
        id_departament = self.request.query_params.get('id_departament', None)
        if id_departament is not None:
            queryset = Cities.objects.filter(id_departament_id=id_departament)
        return queryset

    @action(detail=True, methods=['POST'])
    def cities_action(self, request, pk=None):
        """use to create and update"""
        """http://127.0.0.1:8000/api/cities/5/cities_action/"""
        print("##############################################################")
        print(pk)
        queryset = Cities.objects.filter(id_departament_id=pk)
        print(queryset)
        """response = {'message': 'Rating update', 'result': serializer.data}"""
        print("##############################################################")
        return queryset


class CitiesFrontViewSet(viewsets.ModelViewSet):
    queryset = Cities.objects.all()
    serializer_class = CitiesSerializer
    authentication_classes = ()
    permission_classes = ()

    def get_queryset(self):
        """http://127.0.0.1:8000/api/cities?id_departament=5"""
        queryset = Cities.objects.all()
        id_departament = self.request.query_params.get('id_departament', None)
        if id_departament is not None:
            queryset = Cities.objects.filter(id_departament_id=id_departament)
        return queryset


class ImagesViewSet(viewsets.ModelViewSet):
    queryset = Images.objects.all()
    serializer_class = ImagesSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """http://127.0.0.1:8000/api/products?id_store=1"""
        queryset = Images.objects.all()
        id_product = self.request.query_params.get('id_product', None)
        if id_product is not None:
            queryset = Images.objects.filter(product_id=id_product)
        return queryset


class GetLastImageViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        id_store = self.request.query_params.get('id_store', None)
        data = []
        url_bucket_docs = settings.AWS_URL_BUCKET_DOCS
        if id_store is not None:
            sql = 'select * from api_documentsstore dc left join api_documenttype tp on tp.id_document_type = dc.documenttype_id  where store_id = ' + \
                str(id_store)
            for p in DocumentsStore.objects.raw(sql):
                data .append({
                    'id_documents': p.id_documents,
                    'url_document': url_bucket_docs + str(p.url_document),
                    'id_document_type': p.id_document_type,
                    'type': p.type
                })
        return Response(data)


class UserFrontViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = ()

    @action(detail=True, methods=['PUT'])
    def users_action_update_store(self, request, pk=None):
        try:
            """use to update users"""
            """example request http://127.0.0.1:8000/api/cities/5/users_action_update/"""
            store = request.data['store']
            user = User.objects.get(id=pk)
            user.store_id = store
            user.save()
            serializer = UserSerializer(user, many=False)
            response = {
                'message': 'User update',
                'result': serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {
                'message': 'Can´t update user'
            }
            return Response(response,
                            status=status.HTTP_400_BAD_REQUEST)


class UserTypeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    @action(detail=True, methods=['PUT'])
    def users_action_update_type(self, request, pk=None):
        try:
            """use to update users"""
            """example request http://127.0.0.1:8000/api/cities/5/users_action_update_type/"""
            type = request.data['type']
            user = User.objects.get(id=pk)
            user.type_user_id = type
            user.save()
            serializer = UserSerializer(user, many=False)
            response = {
                'message': 'User update',
                'result': serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {
                'message': 'Can´t update user'
            }
            return Response(response,
                            status=status.HTTP_400_BAD_REQUEST)

class ValidateUserExist(viewsets.ViewSet):
    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = ()

    def list(self, request):
        get_user_name = self.request.query_params.get('username', None)
        user_info = User.objects.filter(username=get_user_name)
        data = ""
        user_exist = ""
        for p in user_info:
            user_exist = p.username

        if user_exist == "":
            data = False
        else:
            data = True

        return Response(data)



class PaymentPercentagesSaleViewSet(viewsets.ViewSet):
    serializer_class = PaymentPercentagesSaleSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    def list(self, request):
        data = []        
        percentages = PaymentPercentages.objects.filter(type_percentage_id=2, state_percentage = True) 
        for p in percentages:
            data .append({
                'id': p.id,
                'percentage': p.percentage,
                'description': p.description,
            })
        return Response(data)

class PercentagesTaxViewSet(viewsets.ViewSet):
    serializer_class = PaymentPercentagesSaleSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    def list(self, request):
        data = []        
        percentages = PaymentPercentages.objects.filter(type_percentage_id=5, state_percentage = True) 
        for p in percentages:
            data .append({
                'id': p.id,
                'percentage': p.percentage,
                'description': p.description,
            })
        return Response(data)



class PaymentPercentagesPaymentViewSet(viewsets.ViewSet):
    serializer_class = PaymentPercentagesSaleSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    def list(self, request):
        data = []        
        percentages = PaymentPercentages.objects.filter(type_percentage_id=1, state_percentage = True) 
        for p in percentages:
            data .append({
                'id': p.id,
                'percentage': p.percentage,
                'description': p.description,
            })
        return Response(data)