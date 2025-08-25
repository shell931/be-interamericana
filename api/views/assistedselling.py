import pdb
from django.core.mail.message import EmailMultiAlternatives
from django.db.models import manager, query
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
from ..models import *
from ..serializers import UserSerializer, GroupSerializer, \
    MenuSerializer, CreateUserSerializer, StoresSerializer, \
    DepartmentsSerializer, CitiesSerializer, ProductsSerializer,\
    CategoriesSerializer, ImagesSerializer, ProductsFrontStoreSerializer, \
    AdminProductSerializer, LocationClientSerializer, LocationClientByUserSerializer, SubCategoriesSerializer, TypeIdentificationSerializer, InvoiceDetalSerializer, InvoiceSerializer, TransactionDataSerializer
from django.contrib.auth.models import Group
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from itertools import chain
from django.db import connection
import json
import collections
import requests
from django.conf import settings
from .transaction import *
import json

def sendAssistedSellingMailCustomer(data):
    for p in data:
        user_mail = p['user_mail']
        reference = p['reference']
        description = p['description']
        total = p['total']
        name_client = p['name_client']
        celphone = p['celphone']
        number_identifier = p['total']
        address = p['address']
        city = p['city']
        name_manager = p['name_manager']
        name_store = p['name_store']
        document_store = p['document_store']
        email_store = p['email_store']
        cellphone_store = p['cellphone_store']
        address_store = p['address_store']
        city_store = p['city_store']
        cod_reply = p['cod_reply']
        num_recibo = p['num_recibo']
        name_state = p['name_state']

    template = get_template('mails/assisted_sell_customer.html')
    subject = 'Has realizado una transaccion - Referencia No. '+ str(reference)

    content = template.render({
                'user_mail': user_mail,
                'reference': reference,
                'description': description,
                'total': total,
                'name_client' : name_client,
                'celphone': celphone,
                'number_identifier' : number_identifier,
                'adress': address,
                'city': city,
                'name_manager': name_manager,
                'name_store': name_store,
                'document_store': document_store,
                'email_store': email_store,
                'cellphone_store' : cellphone_store,
                'address_store': address_store,
                'city_store': city_store,
                'cod_reply': cod_reply,
                'num_recibo': num_recibo,
                'name_state': name_state,
    })

    message = EmailMultiAlternatives(subject,  # Titulo
                                    '',
                                    settings.EMAIL_HOST_USER,  # Remitente
                                    to=[
                                        user_mail
                                    ])  # Destinatario
    message.attach_alternative(content, 'text/html')
    message.send()
    response = {
        'message': 'Email Send',
    }
    return response

def sendAssistedSellingMailStore(data):
    for p in data:
        user_mail = p['user_mail']
        reference = p['reference']
        description = p['description']
        total = p['total']
        name_client = p['name_client']
        celphone = p['celphone']
        number_identifier = p['total']
        address = p['address']
        city = p['city']
        name_manager = p['name_manager']
        name_store = p['name_store']
        document_store = p['document_store']
        email_store = p['email_store']
        cellphone_store = p['cellphone_store']
        address_store = p['address_store']
        city_store = p['city_store']
        cod_reply = p['cod_reply']
        num_recibo = p['num_recibo']
        name_state = p['name_state']
        reference_tx = p['reference_tx']
        date_tx = p['date_tx']
        get_num_aprob = p['get_num_aprob']
        

    template = get_template('mails/assisted_sell_store.html')
    content = template.render({
                'user_mail': user_mail,
                'reference': reference,
                'description': description,
                'total': total,
                'name_client' : name_client,
                'celphone': celphone,
                'number_identifier' : number_identifier,
                'adress': address,
                'city': city,
                'name_manager': name_manager,
                'name_store': name_store,
                'document_store': document_store,
                'email_store': email_store,
                'cellphone_store' : cellphone_store,
                'address_store': address_store,
                'city_store': city_store,
                'cod_reply': cod_reply,
                'num_recibo': num_recibo,
                'name_state': name_state,
                'reference_tx': reference_tx,
                'date_tx' : date_tx,
                'get_num_aprob' : get_num_aprob
    })

    subject = 'Has realizado una transacción No. ' +str(reference)
    message = EmailMultiAlternatives(subject,  # Titulo
                    '',
                        settings.EMAIL_HOST_USER,  # Remitente
                        to=[
                            email_store
                        ])  # Destinatario
    message.attach_alternative(content, 'text/html')
    message.send()

    subject = 'Transacción No. ' +str(reference)
    message = EmailMultiAlternatives(subject,  # Titulo
                    '',
                        settings.EMAIL_HOST_USER,  # Remitente
                        to=[
                            settings.EMAIL_ADMIN
                        ])  # Destinatario
    message.attach_alternative(content, 'text/html')
    message.send()



    response = {'messaje': 'Send email', 'result': 200}
    return response

class SetAssitedSelling(viewsets.ViewSet):
    """
    View to set store.
    """
    authentication_classes = ()
    permission_classes = ()

    def create(self, request):
        # try:
        # GET DATA REQUEST
        quot = request.data.get("quot")
        card_number = request.data.get("card_number")
        month = request.data.get("month")
        year = request.data.get("year")
        cvv = request.data.get("cvv")
        total_tx = request.data.get("total_tx")
        tag_first_name = request.data.get("tag_first_name")
        tag_last_name = request.data.get("tag_last_name")
        tag_type_identification = request.data.get("tag_type_identification")
        tag_number_identification = request.data.get(
            "tag_number_identification")
        tag_email = request.data.get("tag_email")
        tag_cellphone = request.data.get("tag_cellphone")
        tag_desc_selling = request.data.get("tag_desc_selling")
        tag_tax_iva = request.data.get("tag_tax_iva")
        tag_store = request.data.get("tag_store")
        brand = request.data.get("brand")
        let_reference = int(round(time.time() * 1000))
        id_user_front = request.data.get("id_user_front")
        selectedCity = request.data.get("selectedCity")
        address = request.data.get("address")

        # CREATE TRANSACTION ON DATABASE
        transaction_assited = TransactionData.objects.create(
            quot=quot,
            total_tx=total_tx,
            tag_first_name=tag_first_name,
            tag_last_name=tag_last_name,
            tag_type_identification=TypeIdentification.objects.get(
                id=tag_type_identification),
            tag_number_identification=tag_number_identification,
            tag_email=tag_email,
            tag_cellphone=tag_cellphone,
            tag_desc_selling=tag_desc_selling,
            tag_tax_iva=PaymentPercentages.objects.get(id=tag_tax_iva),
            tag_store=Stores.objects.get(id_store=tag_store),
            reference=let_reference,
            type_transaction=TypeTransaction.objects.get(id=2),
            brand=brand
        )
        transaction_assited.save()

        idTransactionData = transaction_assited.id
        referenceTransaction = transaction_assited.reference

        iva = PaymentPercentages.objects.filter(
            type_percentage_id=5).values('percentage')
        iva = iva[0]['percentage']

        base_tax = PaymentPercentages.objects.filter(
            type_percentage_id=7).values('percentage')
        base_tax = base_tax[0]['percentage']

        # CALC TAXABLE BASE 
        taxable_base = total_tx / base_tax
        # CALC TOTAL IVA 
        total_iva = (
            taxable_base * iva) / 100

        #import pdb; pdb.set_trace()

        # GET RETE ICA
        reteica = PaymentPercentages.objects.filter(
            type_percentage_id=3).values('percentage')
        reteica = reteica[0]['percentage']
        val_reteica = (taxable_base * reteica) / 100    

        # GET RETE FUENTE
        retefuente = PaymentPercentages.objects.filter(
            type_percentage_id=4).values('percentage')
        retefuente = retefuente[0]['percentage']
        val_retefuente = (taxable_base * retefuente) / 100

        # GET RETE FUENTE
        reteiva = PaymentPercentages.objects.filter(
            type_percentage_id=6).values('percentage')
        reteiva = reteiva[0]['percentage']
        val_reteiva = (total_iva * reteiva) / 100

        # GET STORE'S PERCENTAGE COMMISION
        get_valus_store = Stores.objects.filter(id_store=tag_store)
        for p in get_valus_store:
            commision_payment = PaymentPercentages.objects.filter(
                id=p.commission_payment_id).values('percentage')
            commision_sale = PaymentPercentages.objects.filter(
                id=p.commission_sale_id).values('percentage')
            # GET COMISION PAYMENT
            get_commision_payment = commision_payment[0]['percentage']
            val_commision_payment = (
                total_tx * get_commision_payment) / 100
            # GET COMISION SELL
            get_commision_sale = commision_sale[0]['percentage']
            val_commision_sale = (
                total_tx * get_commision_sale) / 100

        # GET COMISSION IVA
        val_percentage_commision_tax = val_commision_payment + val_commision_sale
        val_percentage_commision_tax = (
            val_percentage_commision_tax * iva) / 100

        # CALC TOTAL BALCE
        total_balance = total_tx - \
            (val_reteica + val_retefuente + val_reteiva + val_commision_payment +
                val_commision_sale + val_percentage_commision_tax)

        # CREATE INVOICE HEADER
        invoiceObject = Invoice.objects.create(
            reference=referenceTransaction,
            reference_invoice=int(round(time.time() * 1000)),
            total_price=total_tx,
            name_client=tag_first_name,
            first_name_client=tag_last_name,
            phone=tag_cellphone,
            number_identifier=tag_number_identification,
            email=tag_email,
            payment_method_id="1",
            state_id=1,
            shipping_voucher="any.any",
            type_identification_id=tag_type_identification,
            user_id=id_user_front,
            id_store_id=tag_store,
            transaction_id=idTransactionData,
            percentage_sale=get_commision_sale,
            val_percentage_sale=val_commision_sale,
            percentage_commision_payment=get_commision_payment,
            val_percentage_commision_payment=val_commision_payment,
            percentage_rete_ica=reteica,
            val_percentage_rete_ica=val_reteica,
            percentage_rete_fuente=retefuente,
            val_percentage_rete_fuente=val_retefuente,
            percentage_commision_tax=iva,
            val_percentage_commision_tax=val_percentage_commision_tax,
            total_balance = total_balance,
            type_service_id = 2,
            adress = address,
            city_id = selectedCity,
            val_percentage_rete_iva = val_reteiva,
            val_tax = total_iva,
            val_taxable_base = taxable_base
        )
        idInvoice = invoiceObject.id

        # CREATE INVOICE DETAIL
        InvoiceDetail.objects.create(
            id_invoice_id=idInvoice,
            name_product=tag_desc_selling,
            description_product=tag_desc_selling,
            unit_price=total_tx,
            quantity=1,
            total_price=total_tx,
            reference=referenceTransaction
        )

        # SEND TRANSACTION TO GATEWAY PAYMENT
        objectTransac000tion = []
        objectTransaction = {
            'quota': quot,
            'billingNames': tag_first_name,
            'billingLastNames': tag_last_name,
            'type_identifier_id': tag_type_identification,
            'webProductsReference': let_reference,
            'typeIdentification': tag_type_identification,
            'identificationNumber': tag_number_identification,
            'brand': brand,
            'txnid': 1,
            'cardNumber': card_number,
            'expiryMonth': month,
            'expiryYear': year,
            'securityCode': cvv,
            'tag_cellphone': tag_cellphone,
            'total_tx': total_tx,
            'tag_email': tag_email,
            'idTransactionData': idTransactionData
        }

        ejecTransaction = SetTransaction
        result_transaction = ejecTransaction.SetTransactionAssisted(objectTransaction)
        # import pdb; pdb.set_trace()

        
        query_reference = Invoice.objects.filter(reference = referenceTransaction)

        for invo in query_reference:
            reference_tx = invo.reference_invoice
            date_tx = invo.created_at

        # Client        
        name_client = tag_first_name+' '+tag_last_name
        city_query = Cities.objects.filter(id_city = selectedCity)

        for index in city_query:
            city = index.city
        
        # Store
        store_query = Stores.objects.filter(id_store=tag_store)
            
        for sto in store_query:
            name_manager = sto.manager
            name_store = sto.name_store
            document_store = sto.number_identifier
            cellphone_store = sto.telephone
            address_store = sto.address
            email_store = sto.email

            city_store_query  = Cities.objects.filter(id_city =  sto.city_id)
            
            for cit in city_store_query:
                city_store = index.city

        # Transaction data

        transaction_query = TransactionData.objects.filter(reference = referenceTransaction)

        for tran in transaction_query:
            print(tran.num_aprob)
            cod_reply = tran.cod_reply
            num_recibo = tran.num_recibo
            get_num_aprob = tran.num_aprob
            
            query_state = TransactionState.objects.filter(id=tran.state_id)
            for sta in query_state:
                name_state = sta.name_state

        data = []
        data.append({
                    'user_mail': tag_email,
                    'reference': referenceTransaction,
                    'description': tag_desc_selling,
                    'total': total_tx,
                    'name_client' : name_client,
                    'celphone': tag_cellphone,
                    'number_identifier' : tag_number_identification,
                    'address': address,
                    'city': city,
                    'name_manager': name_manager,
                    'name_store': name_store,
                    'document_store': document_store,
                    'email_store': email_store,
                    'cellphone_store' : cellphone_store,
                    'address_store': address_store,
                    'city_store': city_store,
                    'cod_reply': cod_reply,
                    'num_recibo': num_recibo,
                    'name_state': name_state,
                    'reference_tx': reference_tx,
                    'date_tx': date_tx,
                    'get_num_aprob': get_num_aprob                    
                     })
        # sendAssistedSellingMailCustomer(data)
        sendAssistedSellingMailStore(data)

        if result_transaction["status"] == 400:
            transaction_up = TransactionData.objects.get(id=transaction_assited.id)
            transaction_up.state_id = 4
            transaction_up.save()
            
            invoice_up = Invoice.objects.get(id=idInvoice)
            invoice_up.state_id = 3
            invoice_up.save()
            
            id_transaction_data = transaction_assited.id
            response = {'id_transaction_data': id_transaction_data, 'result': 200}
            return Response(response, status=status.HTTP_200_OK)                    
            
        else:

            if result_transaction["codreply"] != '00': 
                invoice_up = Invoice.objects.get(id=idInvoice)
                invoice_up.state_id = 2
                invoice_up.save()

            id_transaction_data = transaction_assited.id
            response = {'id_transaction_data': id_transaction_data, 'result': 200}
            return Response(response, status=status.HTTP_200_OK)

        # except:
        #     response = {'message': 'Store no create', 'result': 400}
        #     return Response(response, status=status.HTTP_400_BAD_REQUEST)
