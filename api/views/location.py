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


class LocationClientViewSet(viewsets.ModelViewSet):
    queryset = LocationClient.objects.all()
    serializer_class = LocationClientSerializer
    authentication_classes = ()
    permission_classes = ()

    def get_queryset(self):
        """http://127.0.0.1:8000/api/location_client?id_user_front=1"""
        id_user_front = self.request.query_params.get('id_user_front', None)
        queryset = LocationClient.objects.filter(user__id=id_user_front)
        return queryset

    @action(detail=True, methods=['POST', 'DELETE', 'PUT'])
    def action_location(self, request, pk=None):
        if request.method == 'DELETE':
            try:
                location = LocationClient.objects.get(id=pk)
                location_user = location.user.all()

                for e in location_user:
                    id_user_front = e.id

                location = LocationClient.objects.get(id=pk)
                location.delete()

                locations = LocationClient.objects.filter(
                    user__id=id_user_front)
                for e in locations:
                    e.predetermined = False
                    e.save()
                count = 1
                for e in locations:
                    if (count == 1):
                        e.predetermined = True
                        e.save()
                    count = count + 1

                response = {
                    'message': 'Location delete correctly',
                    'result': 200
                }
                return Response(response, status=status.HTTP_200_OK)
            except:
                response = {
                    'message': 'No delete location or bad request',
                    'result': 400
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'PUT':
            try:
                city = request.data['city']
                neighborhood = request.data['neighborhood']
                via = request.data['via']
                number = request.data['number']
                sn = request.data['number']
                additional_data = request.data['additional_data']
                phone = request.data['phone']
                contact = request.data['contact']

                location = LocationClient.objects.get(id=pk)
                location.city_id = city
                location.neighborhood = neighborhood
                location.via = via
                location.number = number
                location.sn = sn
                location.additional_data = additional_data
                location.phone = phone
                location.contact = contact
                location.save()
                response = {
                    'message': 'Location update correctly',
                    'result': 200
                }
                return Response(response, status=status.HTTP_200_OK)
            except:
                response = {
                    'message': 'No update location or bad request',
                    'result': 400
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)


class LocationClientByUserViewSet(viewsets.ViewSet):
    serializer_class = LocationClientByUserSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        id_user_front = self.request.query_params.get('id_user_front', None)
        data = []
        sql = 'select l.id,l.neighborhood, l.number, l.via, l.sn, l.additional_data, l.phone, l.contact,l.predetermined,c.city as nameci, d.departament from api_locationclient l ' \
              'join api_locationclient_user lu on lu.locationclient_id = l.id ' \
              'join api_cities c on c.id_city = l.city_id ' \
              'join api_departments d on d.id_departament  = c.id_departament_id ' \
              'where lu.user_id = '+ id_user_front
        for p in LocationClient.objects.raw(sql):
            data.append({
                'id': p.id,
                'neighborhood': p.neighborhood,
                'number': p.number,
                'via': p.via,
                'sn': p.sn,
                'additional_data': p.additional_data,
                'phone': p.phone,
                'nameci': p.nameci,
                'departament': p.departament,
                'contact': p.contact,
                'predetermined': p.predetermined
            })
        return Response(data)


class LocationClientByIdViewSet(viewsets.ViewSet):
    serializer_class = LocationClientByUserSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        id_location = self.request.query_params.get('id_location', None)
        data = []
        sql = 'select l.id,l.via, l.sn, l.additional_data, l.phone, l.contact, c.id_city, c.city as nameci, d.departament, d.id_departament from api_locationclient l ' \
              'join api_locationclient_user lu on lu.locationclient_id = l.id ' \
              'join api_cities c on c.id_city = l.city_id ' \
              'join api_departments d on d.id_departament  = c.id_departament_id where l.id = '+id_location
        jsonData = ''
        for p in LocationClient.objects.raw(sql):
            jsonData = {
                'id': p.id,
                'neighborhood': p.neighborhood,
                'number': p.number,
                'via': p.via,
                'sn': p.sn,
                'additional_data': p.additional_data,
                'phone': p.phone,
                'id_city': p.id_city,
                'nameci': p.nameci,
                'id_departament': p.id_departament,
                'departament': p.departament,
                'contact': p.contact
            }

        return Response(jsonData)


class LocationCheckoutClientViewSet(viewsets.ModelViewSet):
    queryset = LocationClient.objects.all()
    serializer_class = LocationClientSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        id_user_front = self.request.query_params.get('id_user_front', None)
        data = []
        sql = 'select l.id,l.neighborhood, l.number, l.via, l.sn, l.additional_data, l.phone, l.contact, c.id_city,c.city as nameci, d.departament, au.email, au.first_name, au.last_name, au.type_identifier_id, au.number_identifier ' \
              'from api_locationclient l ' \
              'join api_locationclient_user lu on lu.locationclient_id = l.id ' \
              'join auth_user au on au.id = lu.user_id ' \
              'join api_cities c on c.id_city = l.city_id ' \
              'join api_departments d on d.id_departament  = c.id_departament_id ' \
              'where lu.user_id = '+ id_user_front + ' and l.predetermined = true'
        for p in LocationClient.objects.raw(sql):
            data.append({
                'id': p.id,
                'neighborhood': p.neighborhood,
                'number': p.number,
                'via': p.via,
                'sn': p.sn,
                'additional_data': p.additional_data,
                'phone': p.phone,
                'id_city': p.id_city,
                'nameci': p.nameci,
                'departament': p.departament,
                'contact': p.contact,
                'email': p.email,
                'first_name': p.first_name,
                'last_name': p.last_name,
                'type_identifier_id': p.type_identifier_id,
                'number_identifier': p.number_identifier
            })
        return Response(data)


class LocationGeneralUpdatesViewSet(viewsets.ModelViewSet):
    queryset = LocationClient.objects.all()
    serializer_class = LocationClientSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    @action(detail=True, methods=['PUT'])
    def action_location(self, request, pk=None):
        if request.method == 'PUT':
            try:
                predetermined = request.data['predetermined']
                id_user_front = request.data['id_user_front']

                locations = LocationClient.objects.filter(
                    user__id=id_user_front)
                for e in locations:
                    e.predetermined = False
                    e.save()
                location = LocationClient.objects.get(id=pk)
                location.predetermined = predetermined
                location.save()

                response = {
                    'message': 'Location update correctly',
                    'result': 200
                }
                return Response(response, status=status.HTTP_200_OK)
            except:
                response = {
                    'message': 'No update location or bad request..',
                    'result': 400
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
