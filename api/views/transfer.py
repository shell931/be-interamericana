from django.core.mail.message import EmailMultiAlternatives
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
import json


class TransferRequestViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def create(self, request):
        # try:
        # GET VALUES
        id_store = request.data.get("id_store")
        balance = 0
        sum_balance = 0
        sum_price_subtrac = 0
        sum_price_subtrac_contra = 0
        
    
        balance_inv_aprobe = Invoice.objects.filter(
            id_store_id=id_store, state_id=4).aggregate(Sum('total_balance'))
        balance_inv_anull = Invoice.objects.filter(
            id_store_id=id_store, state_id=7, paid_trade=True).aggregate(Sum('total_price'))
        balance_inv_contra = Invoice.objects.filter(
            id_store_id=id_store, state_id=11, paid_trade=True).aggregate(Sum('total_price'))


        if balance_inv_aprobe['total_balance__sum'] is not None:
            sum_balance = balance_inv_aprobe['total_balance__sum']
        if balance_inv_anull['total_price__sum'] is not None:
            sum_price_subtrac = balance_inv_anull['total_price__sum']
        if balance_inv_contra['total_price__sum'] is not None:
            sum_price_subtrac_contra = balance_inv_contra['total_price__sum']

        balance = sum_balance - (sum_price_subtrac + sum_price_subtrac_contra)
        # discount_back = (balance*5)/100
        discount_back = 0
        balance = balance - discount_back

        get_accountbank_data = BankAccounts.objects.get(store_id=id_store)

        # CREATE TRANSFER OBJECT
        obj_transfe = Transfers.objects.create(
            account_number=get_accountbank_data.account_number,
            responsible=get_accountbank_data.responsible,
            val_request=balance,
            val_transfer=balance,
            val_commision_bank=0,
            val_commision_transfe=0,
            bank=Banks.objects.get(id_bank=get_accountbank_data.bank_id),
            typeaccount=TypeAccount.objects.get(
                id_type_account=get_accountbank_data.typeaccount_id),
            store=Stores.objects.get(id_store=id_store),
            state=TransferState.objects.get(id=1),
            reference=int(round(time.time() * 1000))
        )
        id_transfe = obj_transfe.id

        # EDIT INVOICE STATUS THAT BELONG TO THIS TRANSFER
        invoices = Invoice.objects.filter(
            id_store_id=id_store, state_id=4).update(state_id=8, transfer_id=id_transfe)

        invoices_anull = Invoice.objects.filter(
            id_store_id=id_store, state_id=7).update(state_id=8, transfer_id=id_transfe)

        invoices_canceled = Invoice.objects.filter(
            id_store_id=id_store, canceled_in_transfer=True).update(state_id=8, transfer_id=id_transfe, canceled_in_transfer = False)

        invoices_contra = Invoice.objects.filter(
            id_store_id=id_store, state_id=11).update(state_id=8, transfer_id=id_transfe)

        response = {'messaje': 'transfer request correctly',
                    'data': id_transfe, 'result': 200}
        return Response(response, status=status.HTTP_200_OK)

        # except:
        #     response = {
        #             'message': 'Bad request',
        #             'result': 400
        #         }
        #     return Response(response, status=status.HTTP_400_BAD_REQUEST)


class GetTransferDataViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):

        try:
            data_transfer = ''
            id_transfe = self.request.query_params.get('id_transfe', None)
            transfer_object = Transfers.objects.get(id=id_transfe)

            data_transfer = {
                'account_number': transfer_object.account_number,
                'responsible': transfer_object.responsible,
                'val_request': transfer_object.val_request,
                'val_transfer': transfer_object.val_transfer,
                'bank': transfer_object.bank.bank,
                'state': transfer_object.state.name_state,
                'store': transfer_object.store.name_store,
                'typeaccount': transfer_object.typeaccount.type_account,
                'reference': transfer_object.reference,
                'created_at': transfer_object.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }

            response = {
                'status': True,
                'data': data_transfer,
                'result': 200
            }

            return Response(response, status=status.HTTP_200_OK)

        except:
            response = {
                'message': 'Bad request',
                'result': 400
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class GetAllTransfersDataViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):

        try:
            data_transfers = []

            id_store = ''
            id_store = self.request.query_params.get('id_store', None)

            if id_store is None:
                transfers_object = Transfers.objects.all().order_by('-id')
            else:
                transfers_object = Transfers.objects.filter(
                    store_id=id_store).order_by('-id')

            for i in transfers_object:
                data_transfers.append({
                    'id': i.id,
                    'reference': i.reference,
                    'account_number': i.account_number,
                    'responsible': i.responsible,
                    'val_request': i.val_request,
                    'val_transfer': i.val_transfer,
                    'bank': i.bank.bank,
                    'state': i.state.name_state,
                    'store': i.store.name_store,
                    'typeaccount': i.typeaccount.type_account,
                    'created_at': i.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'state_id': i.state_id,
                })

            response = {
                'status': True,
                'data': data_transfers,
                'result': 200
            }

            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {
                'message': 'Bad request',
                'result': 400
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class UpdateStatusTransferViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def update(self, request, pk=None):
        try:
            state = request.data.get("state")

            if state == 2:
                # TRANSFER APROBE
                transfer_up = Transfers.objects.get(id=pk)
                transfer_up.state = TransferState.objects.get(id=state)
                transfer_up.save()

                # CHANGE INVOICE'S STATUS
                invoices_state_transfer = Invoice.objects.filter(
                    transfer_id=pk, state_id=8).update(state_id=9, paid_trade = True)

                invoices_canceled = Invoice.objects.filter(
                    transfer_id=pk, canceled=True).update(state_id=10, paid_trade = True )
                
                invoices_state_contra = Invoice.objects.filter(
                    transfer_id=pk, contra=True).update(state_id=12, paid_trade = True)
                    

                response = {
                    'message': 'Percentages update correctly',
                    'result': 200
                }
            elif state == 3:
                # CHANGE TRANFER REGECTED
                # CHANGE TRANSFER STATUS
                transfer_up = Transfers.objects.get(id=pk)
                transfer_up.state = TransferState.objects.get(id=state)
                transfer_up.save()

                # CHANGE INVOICE'S STATUS
                invoices = Invoice.objects.filter(
                    transfer_id=pk).update(state_id=4)

                invoices_canceled = Invoice.objects.filter(
                    transfer_id=pk, canceled=True).update(state_id=7)

                invoices_canceled = Invoice.objects.filter(
                    transfer_id=pk, contra=True).update(state_id=11)

                response = {
                    'message': 'Percentages update correctly',
                    'result': 200
                }

            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {
                'message': 'Bad request',
                'result': 400
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class sendEmailTransferRequestViewSet (viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()

    def create(self, request):
        try:
            template = get_template('mails/transfer_request.html')
            id_store = request.data['id_store']
            id_transfer = request.data['id_transfer']
            store_data = Stores.objects.filter(id_store=id_store)
            transfer_data = Transfers.objects.get(id=id_transfer)
            subject = 'Hemos recibido tu solicitud de transferencia - '+transfer_data.reference
            for sto in store_data:
                store_email = sto.email
            content = template.render({
                'store_email': store_email,
                'web_url': settings.WEB_URL,
                'reference': transfer_data.reference,
            })
            message = EmailMultiAlternatives(subject,  # Titulo
                                             '',
                                             settings.EMAIL_HOST_USER,  # Remitente
                                             to=[
                                                 store_email
                                             ])  # Destinatario
            response = {
                'message': 'Email Send',
            }
            message.attach_alternative(content, 'text/html')
            message.send()
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {
                'message': 'Can´t send email  '
            }
            return Response(response,
                            status=status.HTTP_400_BAD_REQUEST)


class sendEmailReplyTransferViewSet (viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()

    def create(self, request):
        try:
            reference = request.data['reference']
            state = request.data['state']
            transfer_data = Transfers.objects.filter(reference=reference)
            for tra in transfer_data:
                store_data = Stores.objects.filter(id_store=tra.store_id)
                for sto in store_data:
                    store_email = sto.email
            if state == 2:
                subject = 'Transferencia Aprobada - '+reference
                template = get_template('mails/transfer_aprobe.html')
                content = template.render({
                    'store_email': store_email,
                    'web_url': settings.WEB_URL,
                    'reference': reference,
                })
                message = EmailMultiAlternatives(subject,  # Titulo
                                                 '',
                                                 settings.EMAIL_HOST_USER,  # Remitente
                                                 to=[
                                                     store_email
                                                 ])  # Destinatario
                message.attach_alternative(content, 'text/html')
                message.send()
            elif state == 3:
                subject = 'Transferencia Rechazada '+reference
                template = get_template('mails/transfer_reject.html')
                content = template.render({
                    'store_email': store_email,
                    'web_url': settings.WEB_URL,
                    'reference': reference,
                })
                message = EmailMultiAlternatives(subject,  # Titulo
                                                 '',
                                                 settings.EMAIL_HOST_USER,  # Remitente
                                                 to=[
                                                     store_email
                                                 ])  # Destinatario

                message.attach_alternative(content, 'text/html')
                message.send()
            response = {
                'message': 'Email Send',
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {
                'message': 'Can´t send email  '
            }
            return Response(response,
                            status=status.HTTP_400_BAD_REQUEST)



class GetTransferDetailViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        try:
            dataInvoice = []
            id_transfe = self.request.query_params.get('id_transfe', None)
            invoiceObject = Invoice.objects.filter(transfer_id=id_transfe)        
            tranferObject = Transfers.objects.get(id=id_transfe)        
            for p in invoiceObject:
                dataInvoice.append({
                    'id_invoice': p.id,
                    'reference_invoice': p.reference_invoice,
                    'created_at': p.created_at,
                    'total_price': p.total_price,
                    'total_balance': p.total_balance,
                    'state': p.state.name_state,                    
                })
            
            response = {
                'status': True,
                'data': dataInvoice,
                'val_request': tranferObject.val_request,
                'val_transfer': tranferObject.val_transfer,
                'result': 200
            }

            return Response(response, status=status.HTTP_200_OK)

        except:
            response = {
                'message': 'Bad request',
                'result': 400
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
