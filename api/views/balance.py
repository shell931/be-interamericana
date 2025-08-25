from rest_framework import viewsets, status
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from ..models import *
from ..serializers import *
from django.contrib.auth.models import Group
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from itertools import chain
from django.db import connection
from django.db.models import Sum


class GetBalanceAccountViewSet(viewsets.ViewSet):    
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        # try:
        data_bankaccounts = ''
        total_balance = 0            
        sum_balance = 0
        sum_price_subtrac = 0
        sum_price_subtrac_contra = 0
        
        id_store = self.request.query_params.get('id_store', None)
        # GET ALL INVOICE'S IN STATUS SEND, SUM BALANCE
        queryset = Invoice.objects.filter(
            id_store_id=id_store, state_id=4).aggregate(Sum('total_balance'))
        # GET ALL INVOICE'S IN STATUS ANULL TRANSACTION, SUBSTRACTION BALANCE
        queryset_inv_anull = Invoice.objects.filter(
            id_store_id=id_store, state_id=7, paid_trade=True).aggregate(Sum('total_price'))

        # GET ALL INVOICE'S IN STATUS CONTRA TRANSACTION, SUBSTRACTION BALANCE
        queryset_inv_contra = Invoice.objects.filter(
            id_store_id=id_store, state_id=11, paid_trade=True).aggregate(Sum('total_price'))



        if queryset['total_balance__sum'] is not None:
            sum_balance = queryset['total_balance__sum']        

        if queryset_inv_anull['total_price__sum'] is not None:
            sum_price_subtrac = queryset_inv_anull['total_price__sum']  
        
        if queryset_inv_contra['total_price__sum'] is not None:
            sum_price_subtrac_contra = queryset_inv_contra['total_price__sum']                    

                
        total_balance = sum_balance - (sum_price_subtrac + sum_price_subtrac_contra)
        # discount_back = (total_balance*5)/100
        discount_back = 0
        total_balance = total_balance - discount_back

        queryset = {
            "total_balance__sum": total_balance
        }
                    
        #GET DATA TO ACCOUNT BANK TRANSFER
        account_bank = BankAccounts.objects.get(store_id=id_store)
        data_bankaccounts = {
            'id_bank_account': account_bank.id_bank_account,
            'account_number': account_bank.account_number,
            'responsible': account_bank.responsible,
            'name_bank': account_bank.bank.bank,
            'type_account': account_bank.typeaccount.type_account,
        }

        response = {
            'status': True,
            'data': queryset,
            'data_bankaccounts': data_bankaccounts,
            'result': 200
        }

        return Response(response, status=status.HTTP_200_OK)

        # except:
        #     response = {
        #             'message': 'Bad request',
        #             'result': 400
        #         }
        #     return Response(response, status=status.HTTP_400_BAD_REQUEST)


class GetBalanceDetailTransactionViewSet(viewsets.ViewSet):    
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        
        id_store = self.request.query_params.get('id_store', None)
        # GET ALL INVOICE'S IN STATUS SEND, SUM BALANCE
        queryset_inv_send = Invoice.objects.filter(
            id_store_id=id_store, state_id=4)
        # GET ALL INVOICE'S IN STATUS ANULL TRANSACTION, SUBSTRACTION BALANCE
        queryset_inv_anull = Invoice.objects.filter(
            id_store_id=id_store, state_id=7, paid_trade=True)
        # GET ALL INVOICE'S IN STATUS CONTRA TRANSACTION, SUBSTRACTION BALANCE
        queryset_inv_contra = Invoice.objects.filter(
            id_store_id=id_store, state_id=11, paid_trade=True)

        data = []
        for p in queryset_inv_send:
            print (p)
            data.append({
                'id': p.id,
                'created_at': p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'reference': p.reference_invoice,
                'state': p.state.name_state,   
                'total_balance': p.total_balance,                                    
            })  
        for p in queryset_inv_anull:
            data.append({
                'id': p.id,
                'created_at': p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'reference': p.reference_invoice,
                'state': p.state.name_state,   
                'total_balance': p.total_price,                                    
            })   
        for p in queryset_inv_contra:
            data.append({
                'id': p.id,
                'created_at': p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'reference': p.reference_invoice,
                'state': p.state.name_state,   
                'total_balance': p.total_price,                                    
            })                            
        response = {
            'status': True,
            'data': data,
            'result': 200
        }
        return Response(response, status=status.HTTP_200_OK)