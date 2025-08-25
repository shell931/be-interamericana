from rest_framework import viewsets, status
import sys
from ..models import *
from rest_framework.response import Response
from ..serializers import UserSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import Group
from rest_framework.decorators import action, api_view


class UserStoreViewSet(viewsets.ViewSet):
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        try:
            id_store = self.request.query_params.get('id_store', None)
            if id_store is not None:
                user = User.objects.get(store_id=id_store)
                print(user.id)
            response = {
                'message': 'Response the user id',
                'user_id': user.id
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {'message': 'fail to get user id'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)



class UpdateGroupUserViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    @action(detail=True, methods=['PUT'])
    def action_user_group(self, request, pk=None):
        if request.method == 'PUT':            
            user_id = pk
            group_id = request.data['group_id']
            
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)

            user_group = User.groups.through.objects.get(user=user)            
            user_group.group = group
            user_group.save()

            response = {
                'message': 'User group update!',
                'user_id': user_id
            }

            response = "dsadsa"

            return Response(response, status=status.HTTP_200_OK)


class UserByIdViewSet(viewsets.ViewSet):
    # serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        try:
            id_user = self.request.query_params.get('id_user', None)
            data = ''
            if id_user is not None:
                user = User.objects.get(id=id_user)
                data = {
                    'id': user.id,
                    'username': user.username, 
                    'password': user.password, 
                    'first_name': user.first_name, 
                    'last_name': user.last_name, 
                    'email': user.email,
                    'is_active': user.is_active, 
                    'group_id': user.group_id, 
                    # 'store': user.store, 
                    # 'type_identifier': user.type_identifier,
                    'number_identifier': user.number_identifier
                    }
            response = {
                'message': 'User data',
                'data': data
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {'message': 'fail to get user id'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def update(self, request, pk=None):    
        # try:
        user_id = pk
        group_id = request.data['group_id']
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        is_active = request.data['is_active']
        email = request.data['email']
        
        user = User.objects.get(id=user_id)
        group = Group.objects.get(id=group_id)

        user_group = User.groups.through.objects.get(user=user)            
        user_group.group = group
        user_group.save()

        userEd = User.objects.get(id=user_id)
        userEd.first_name = first_name
        userEd.last_name = last_name
        userEd.is_active = is_active
        userEd.username = email
        userEd.email = email
        userEd.save()

        response = {
            'message': 'User  update',
            'result': 200,
        }
        return Response(response, status=status.HTTP_200_OK)
        # except:
        #     response = {'message': 'No find state', 'result': 400}
        #     return Response(response, status=status.HTTP_400_BAD_REQUESTstate)