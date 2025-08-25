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

class ListInvoiceViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        id_store = request.data.get("id_store")
        id_invoice = request.data.get("id_invoice")
        if id_store is not None:
            sql = 'select inv.*, ci.city as nameci, dep.departament, st.name_store, ap.paymentmethod, sta.name_state, iden.type_identifier, tys.service from api_invoice inv ' \
                'left join api_cities ci on ci.id_city = inv.city_id '\
                'left join api_departments dep on dep.id_departament = ci.id_departament_id '\
                'left join api_stores st on st.id_store = inv.id_store_id ' \
                'left join api_paymentmethod ap on ap.id = inv.payment_method_id ' \
                'left join api_invoicestate sta on sta.id = inv.state_id '\
                'left join api_typeidentification iden on iden.id = inv.type_identification_id '\
                'left join api_typeservices tys on tys.id = inv.type_service_id '\
                'where inv.id_store_id = '+id_store +''\
                'order by id desc'
        else:
            if id_invoice is not None:
                sql = 'select inv.*, ci.city as nameci, dep.departament, st.name_store, ap.paymentmethod, sta.name_state, iden.type_identifier, tys.service from api_invoice inv ' \
                    'left join api_cities ci on ci.id_city = inv.city_id '\
                    'left join api_departments dep on dep.id_departament = ci.id_departament_id '\
                    'left join api_stores st on st.id_store = inv.id_store_id ' \
                    'left join api_paymentmethod ap on ap.id = inv.payment_method_id ' \
                    'left join api_invoicestate sta on sta.id = inv.state_id '\
                    'left join api_typeidentification iden on iden.id = inv.type_identification_id '\
                    'left join api_typeservices tys on tys.id = inv.type_service_id '\
                    'where inv.id = '+id_invoice+''\
                    'order by id desc'
            else:
                sql = 'select inv.*, ci.city as nameci, dep.departament, st.name_store, ap.paymentmethod, sta.name_state, iden.type_identifier, tys.service from api_invoice inv ' \
                    'left join api_cities ci on ci.id_city = inv.city_id '\
                    'left join api_departments dep on dep.id_departament = ci.id_departament_id '\
                    'left join api_stores st on st.id_store = inv.id_store_id ' \
                    'left join api_paymentmethod ap on ap.id = inv.payment_method_id ' \
                    'left join api_invoicestate sta on sta.id = inv.state_id '\
                    'left join api_typeidentification iden on iden.id = inv.type_identification_id '\
                    'left join api_typeservices tys on tys.id = inv.type_service_id '\
                    'order by id desc'
        data = []
        for p in Invoice.objects.raw(sql):
            ScoreValdation = 0
            if p.check_call_control == True and p.check_record == True and p.check_shipment == True and p.check_finaly == True:
                ScoreValdation = 100 
            if p.check_call_control == True and p.check_record == True and p.check_shipment == True and p.check_finaly == False:
                ScoreValdation = 75 
            if p.check_call_control == True and p.check_record == True and p.check_shipment == False and p.check_finaly == False:                
                ScoreValdation = 50
            if p.check_call_control == True and p.check_record == False and p.check_shipment == False and p.check_finaly == False:
                ScoreValdation = 25

            getBinnacleFalse = Binnacle.objects.filter(id_invoice=p.id, check_binnacle_adm = False).count()

            data.append({
                'id': p.id,
                'created_at': p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'reference': p.reference,
                'reference_invoice': p.reference_invoice,
                'total_price': p.total_price,
                'percentage_sale': p.percentage_sale,
                'val_percentage_sale': p.val_percentage_sale,
                'percentage_commision_payment': p.percentage_commision_payment,
                'val_percentage_commision_payment': p.val_percentage_commision_payment,
                'percentage_rete_ica': p.percentage_rete_ica,
                'val_percentage_rete_ica': p.val_percentage_rete_ica,
                'percentage_rete_fuente': p.percentage_rete_fuente,
                'val_percentage_rete_fuente': p.val_percentage_rete_fuente,
                'percentage_commision_tax': p.percentage_commision_tax,
                'val_percentage_commision_tax': p.val_percentage_commision_tax,
                'total_balance': p.total_balance,
                'name_client': p.name_client,
                'first_name_client': p.first_name_client,
                'phone': p.phone,
                'adress': p.adress,
                'number_identifier': p.number_identifier,
                'email': p.email,
                'id_store_id': p.id_store_id,
                'state_id': p.state_id,
                'user_id': p.user_id,
                'transaction_id': p.transaction_id,
                'nameci': p.nameci,
                'departament': p.departament,
                'name_store': p.name_store,
                'paymentmethod': p.paymentmethod,
                'name_state': p.name_state,
                'type_identifier': p.type_identifier,
                'canceled': p.canceled, 
                'service': p.service,
                'join_name': p.name_client +' '+ p.first_name_client,
                'ScoreValdation': ScoreValdation,
                'getBinnacleFalse': getBinnacleFalse
            })
        return Response(data)



class ListInvoiceUserViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        id_user = self.request.query_params.get('id_user', None)
    
        sql = ' SELECT inv.user_id, inv.reference, '\
            'SUM(inv.total_price) as total_p, '\
            'MAX(inv.name_client) as name_client, '\
            'MAX(inv.first_name_client) as first_name_client, '\
            'MAX(inv.phone) as phone, '\
            'MAX(inv.adress) as adress, '\
            'MAX(inv.number_identifier) as number_identifier, '\
            'MAX(inv.email) as email, '\
            'MAX(pay.paymentmethod) as paymentmethod, '\
            'MAX(stinv.name_state) as name_state, '\
            'MAX(stextinv.name_state) as name_external_state, '\
            'MAX(stextinv.id) as ex_state_id, '\
            'MAX(inv.created_at) as created_at, '\
            '1 as id, '\
            'MAX(ci.city) as nameci, '\
            'MAX(dep.departament) as depart, '\
            'MAX(ti.type_identifier) as type_identifier, '\
            'COUNT(inv.id) as total_invoices '\
            'FROM api_invoice as inv '\
            'LEFT JOIN api_cities ci ON ci.id_city = inv.city_id '\
            'LEFT JOIN api_departments dep ON dep.id_departament = ci.id_departament_id '\
            'LEFT JOIN api_paymentmethod pay ON pay.id = inv.payment_method_id '\
            'LEFT JOIN api_invoicestate stinv ON stinv.id = inv.state_id '\
            'LEFT JOIN api_invoiceexternalstate stextinv ON stextinv.id = inv.external_state_id '\
            'LEFT JOIN auth_user us ON us.id = inv.user_id '\
            'LEFT JOIN api_typeidentification ti ON ti.id = us.type_identifier_id '\
            'WHERE user_id = '+id_user+' '\
            'GROUP BY inv.user_id, inv.reference '\
            'ORDER BY inv.reference DESC '\


        data = []
        for p in Invoice.objects.raw(sql):
            data.append({
                'user_id': p.user_id,
                'reference': p.reference,
                'total_p': p.total_p,
                'name_client': p.name_client,
                'first_name_client': p.first_name_client,
                'phone': p.phone,
                'adress': p.adress,
                'number_identifier': p.number_identifier,
                'email': p.email,
                'nameci': p.nameci,
                'depart': p.depart,
                'paymentmethod': p.paymentmethod,
                'name_state': p.name_state,
                'created_at': p.created_at,
                'type_identifier': p.type_identifier,
                'name_external_state' : p.name_external_state,
                'ex_state_id' : p.ex_state_id                
            })
        return Response(data)


class ListInvoiceDetailUserViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        reference = self.request.query_params.get('reference', None)

        # reference = 1621001626180
    
        sql = " select * from api_invoicedetail as invdet "\
            "left join api_products pr on pr.id_product = invdet.id_product_id "\
            "where invdet.reference = '"+ str(reference) +"' "\


        data = []
        for p in Invoice.objects.raw(sql):
            data.append({
                'id': p.id,
                'created_at': p.created_at,
                'unit_price': p.unit_price,
                'quantity': p.quantity,
                'total_price': p.total_price,
                'id_invoice_id': p.id_invoice_id,
                'id_product_id': p.id_product_id,

                'name_product': p.name_product,
                'description_product': p.description_product,
                'product_code': p.product_code,
                'brand': p.brand,
                'image': p.image,
            })
        return Response(data)



class InvoiceByStoreViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    authentication_classes = ()
    permission_classes = ()

    def get_queryset(self):
        """http://127.0.0.1:8000/api/invoice_by_store?id_store=29"""
        queryset = Invoice.objects.all()
        id_store = self.request.query_params.get('id_store', None)
        if id_store is not None:
            sql = 'select inv.*, ci.city as nameci, dep.departament, st.name_store, ap.paymentmethod, sta.name_state, iden.type_identifier, trd.quot, trd.brand, trd.num_aprob, trd.cod_reply, trd.messaje_reply, trd.num_recibo, ts.service from api_invoice inv ' \
                'left join api_cities ci on ci.id_city = inv.city_id '\
                'left join api_departments dep on dep.id_departament = ci.id_departament_id '\
                'left join api_stores st on st.id_store = inv.id_store_id ' \
                'left join api_paymentmethod ap on ap.id = inv.payment_method_id ' \
                'left join api_invoicestate sta on sta.id = inv.state_id '\
                'left join api_typeidentification iden on iden.id = inv.type_identification_id '\
                'left join api_transactiondata trd on trd.id = inv.transaction_id '\
                'left join api_typeservices ts on ts.id = inv.type_service_id '\
                'where inv.id_store_id = '+id_store +' '\
                'order by id desc'
            data = []
            for p in Invoice.objects.raw(sql):
                getBinnacleFalse = Binnacle.objects.filter(id_invoice=p.id, check_binnacle = False).count()
                data.append({
                    'id': p.id,
                    'created_at': p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'reference': p.reference,
                    'reference_invoice': p.reference_invoice,
                    'total_price': p.total_price,
                    'percentage_sale': p.percentage_sale,
                    'val_percentage_sale' : p.val_percentage_sale,
                    'percentage_commision_payment': p.percentage_commision_payment,
                    'val_percentage_commision_payment': p.val_percentage_commision_payment,
                    'percentage_rete_ica': p.percentage_rete_ica,
                    'val_percentage_rete_ica': p.val_percentage_rete_ica,
                    'percentage_rete_fuente': p.percentage_rete_fuente,
                    'val_percentage_rete_fuente': p.val_percentage_rete_fuente,
                    'percentage_commision_tax': p.percentage_commision_tax,
                    'val_percentage_commision_tax': p.val_percentage_commision_tax,
                    'total_balance': p.total_balance,
                    'name_client': p.name_client,
                    'first_name_client': p.first_name_client,
                    'phone': p.phone,
                    'adress': p.adress,
                    'number_identifier': p.number_identifier,
                    'email': p.email,
                    'id_store_id': p.id_store_id,
                    'state_id': p.state_id,
                    'user_id': p.user_id,
                    'transaction_id': p.transaction_id,
                    'nameci': p.nameci,
                    'departament': p.departament,
                    'name_store': p.name_store,
                    'paymentmethod': p.paymentmethod,
                    'name_state': p.name_state,
                    'type_identifier': p.type_identifier,
                    'quot': p.quot,
                    'brand': p.brand,
                    'num_aprob': p.num_aprob,
                    'cod_reply': p.cod_reply,
                    'messaje_reply': p.messaje_reply,
                    'num_recibo': p.num_recibo,
                    'canceled': p.canceled,
                    'type_service': p.service,
                    'type_service_id': p.type_service_id,
                    'getBinnacleFalse': getBinnacleFalse
                })
        return data



class InvoiceHeaderViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        invoice_id = self.request.query_params.get('invoice_id', None)        
        sql = "select inv.*, cit.city as namecity, dep.departament, ti.type_identifier, st.name_store, paym.paymentmethod, sti.name_state, sti.id as state_id, ts.service, tx.quot, tx.brand, tx.num_aprob, tx.cod_reply, tx.messaje_reply,tx.reference, tx.total_tx,tx.num_recibo, tx.tag_cellphone, tx.tag_desc_selling, tx.tag_email, tx.tag_first_name, tx.tag_last_name, tx.tag_number_identification, tx.tag_tax_iva_id, tx.created_at as date_tx,   txi.field from api_invoice inv "\
            "left join api_cities cit on cit.id_city = inv.city_id "\
            "left join api_departments dep on dep.id_departament = cit.id_departament_id "\
            "left join api_typeidentification ti on ti.id = inv.type_identification_id "\
            "left join api_stores st on st.id_store = inv.id_store_id "\
            "left join api_paymentmethod paym on paym.id = inv.payment_method_id  "\
            "left join api_invoicestate sti on sti.id = inv.state_id  "\
            "left join api_typeservices ts on ts.id = inv.type_service_id  "\
            "left join api_transactiondata tx on tx.id = inv.transaction_id  "\
            "left join api_trxinf txi on txi.tx_id = tx.id  "\
            "where inv.id = '"+ invoice_id +"' "\
        
        getBinnacleFalse = Binnacle.objects.filter(id_invoice=invoice_id, check_binnacle_adm = False).count()

        data = []
        for p in Invoice.objects.raw(sql):
            get_field = ""
            if p.field != None:
                get_field = p.field[-4:],
            data = {
                'id': p.id,
                'reference': p.reference,
                'total_price': p.total_price,
                'percentage_sale': p.percentage_sale,
                'val_percentage_sale' : p.val_percentage_sale,
                'percentage_commision_payment': p.percentage_commision_payment,
                'val_percentage_commision_payment': p.val_percentage_commision_payment,
                'percentage_rete_ica': p.percentage_rete_ica,
                'val_percentage_rete_ica': p.val_percentage_rete_ica,
                'percentage_rete_fuente': p.percentage_rete_fuente,
                'val_percentage_rete_fuente': p.val_percentage_rete_fuente,
                'percentage_commision_tax': p.percentage_commision_tax,
                'val_percentage_commision_tax': p.val_percentage_commision_tax,
                'total_balance': p.total_balance,
                'name_client': p.name_client,
                'first_name_client': p.first_name_client,
                'phone': p.phone,
                'adress': p.adress,
                'number_identifier': p.number_identifier,
                'email': p.email,
                'reference_invoice': p.reference_invoice,
                'shipping_voucher': str(p.shipping_voucher),
                'letter_received': str(p.letter_received),
                'reference_invoice': p.reference_invoice,
                'namecity': p.namecity,
                'departament': p.departament,
                'type_identifier': p.type_identifier,
                'name_store': p.name_store,
                'paymentmethod': p.paymentmethod,
                'name_state': p.name_state,
                'state_id': str(p.state_id),                
                'type_service_id': str(p.type_service_id),                
                'service': str(p.service),
                'quot': p.quot,
                'brand': p.brand,
                'num_aprob': p.num_aprob,
                'cod_reply': p.cod_reply,
                'messaje_reply': p.messaje_reply,
                'reference': p.reference,
                'total_tx': p.total_tx,
                'num_recibo': p.num_recibo,
                'tag_cellphone': p.tag_cellphone,
                'tag_desc_selling': p.tag_desc_selling,
                'tag_email': p.tag_email,
                'tag_first_name': p.tag_first_name,
                'tag_last_name': p.tag_last_name,
                'tag_number_identification': p.tag_number_identification,
                'tag_tax_iva_id': p.tag_tax_iva_id,
                'field': get_field,
                'date_tx': p.date_tx.strftime("%Y-%m-%d %H:%M:%S") if p.date_tx else None,                
                'check_call_control': p.check_call_control,
                'check_record': p.check_record,
                'check_shipment': p.check_shipment,
                'check_finaly': p.check_finaly,
                'val_percentage_rete_iva': p.val_percentage_rete_iva,
                'getBinnacleFalse': getBinnacleFalse,                
            }    
        return Response(data)


class InvoiceDetailViewSet(viewsets.ModelViewSet):
    queryset = InvoiceDetail.objects.all()
    serializer_class = InvoiceDetalSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        reference = self.request.query_params.get('reference', None)
        id_search_invoice = self.request.query_params.get('id_invoice', None)    
        sql = " select invdet.*, pr.*, invdet.name_product as name_pr  from api_invoicedetail as invdet "\
            "left join api_products pr on pr.id_product = invdet.id_product_id "\
            "where invdet.id_invoice_id = '"+ id_search_invoice +"' "\


        data = []
        for p in Invoice.objects.raw(sql):
            data.append({
                'id': p.id,
                'created_at': p.created_at,
                'unit_price': p.unit_price,
                'quantity': p.quantity,
                'total_price': p.total_price,
                'id_invoice_id': p.id_invoice_id,
                'id_product_id': p.id_product_id,
                'name_product': p.name_product,
                'description_product': p.description_product,
                'product_code': p.product_code,
                'brand': p.brand,
                'image': p.image,
                'name_pr': p.name_pr
            })
        return Response(data)


class UpdateStatusInvoiceViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def update(self, request, pk=None):    
        state = request.data['state']
        external_state = request.data['external_state']
        try:
            invoice_status = Invoice.objects.get(id=pk)
            invoice_status.state_id = state
            invoice_status.external_state_id = external_state
            invoice_status.save()
            response = {
                'message': 'Invoice status update',
                'result': 200,
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {'message': 'No find state', 'result': 400}
            return Response(response, status=status.HTTP_400_BAD_REQUESTstate)


class UpdateShippingVoucherViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def create(self, request):    

        shipping_voucher = request.data['shipping_voucher']
        id_invoice = request.data['id_invoice']
        
        try:
            invoice = Invoice.objects.get(id=id_invoice)
            invoice.shipping_voucher = shipping_voucher
            invoice.save()
            response = {
                'message': 'Invoice shipping voucher update',
                'result': 200,
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {'message': 'No find state', 'result': 400}
            return Response(response, status=status.HTTP_400_BAD_REQUESTstate)

class UpdateLetterReceivedViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def create(self, request):    
        letter_received = request.data['letter_received']
        id_invoice = request.data['id_invoice']
        
        try:
            invoice = Invoice.objects.get(id=id_invoice)
            invoice.letter_received = letter_received
            invoice.save()
            response = {
                'message': 'Invoice shipping voucher update',
                'result': 200,
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {'message': 'No find state', 'result': 400}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

class InvoiceInProcesReturnViewSet(viewsets.ModelViewSet):
    queryset = InvoiceDetail.objects.all()
    serializer_class = InvoiceDetalSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        id_store = self.request.query_params.get('id_store', None)    
        number_invoice = Invoice.objects.filter(id_store_id=id_store, state_id=1).count()
        return Response(number_invoice)


class UpdateCheckCallControllInvoiceViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def update(self, request, pk=None):            
        check = request.data['check']
        try:
            invoice_status = Invoice.objects.get(id=pk)
            invoice_status.check_call_control = check
            invoice_status.save()
            response = {
                'message': 'Invoice check update',
                'result': 200,
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {'message': 'No update check', 'result': 400}
            return Response(response, status=status.HTTP_400_BAD_REQUESTstate)

class UpdateCheckRecordnvoiceViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def update(self, request, pk=None):            
        check = request.data['check']
        try:
            invoice_status = Invoice.objects.get(id=pk)
            invoice_status.check_record = check
            invoice_status.save()
            response = {
                'message': 'Invoice check update',
                'result': 200,
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {'message': 'No update check', 'result': 400}
            return Response(response, status=status.HTTP_400_BAD_REQUESTstate)


class UpdateCheckShipmentInvoiceViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def update(self, request, pk=None):            
        check = request.data['check']
        try:
            invoice_status = Invoice.objects.get(id=pk)
            invoice_status.check_shipment = check
            invoice_status.save()
            response = {
                'message': 'Invoice check update',
                'result': 200,
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {'message': 'No update check', 'result': 400}
            return Response(response, status=status.HTTP_400_BAD_REQUESTstate)

class UpdateCheckFinalyInvoiceViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def update(self, request, pk=None):            
        check = request.data['check']
        try:
            invoice_status = Invoice.objects.get(id=pk)
            invoice_status.check_finaly = check
            invoice_status.state_id = 4
            invoice_status.save()
            response = {
                'message': 'Invoice check update',
                'result': 200,
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {'message': 'No update check', 'result': 400}
            return Response(response, status=status.HTTP_400_BAD_REQUESTstate)


class GetCheckInvoiceViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        id_invoice = self.request.query_params.get('id_invoice', None)    
        check_validate = self.request.query_params.get('check_validate', None)    
        print(check_validate)
        check_invoice = Invoice.objects.get(id=id_invoice)        
        inv_ch = ''
        if check_validate == '1':                        
            inv_ch = check_invoice.check_call_control
        if check_validate == '2': 
            inv_ch = check_invoice.check_record
        if check_validate == '3': 
            inv_ch = check_invoice.check_shipment
        if check_validate == '4': 
            inv_ch = check_invoice.check_finaly
        
        return Response(inv_ch)

class GetListBinnacles(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def list(self, request):
        id_invoice = self.request.query_params.get('id')             
        type = self.request.query_params.get('type') 
        if(type=='st'):
            Binnacle.objects.filter(id_invoice=id_invoice).update(check_binnacle=True)
        else:
            Binnacle.objects.filter(id_invoice=id_invoice).update(check_binnacle_adm=True)
        
        sql = Binnacle.objects.filter(id_invoice=id_invoice).order_by('-id')
        data = []
        for p in sql:
            data.append({
                'id': p.id,
                'created_at': p.created_at,
                'observation': p.observation,
                'id_invoice': p.id_invoice.id,
                'user_id': p.user.username
            })
        if data:
            response = {'message': 'Find Binnacles', 'result': 200, 'data': data}
            return Response(response,status=status.HTTP_200_OK)
        else:
            response = {'message': 'No Find Binnacles', 'result': 400}
            return Response(response,status=status.HTTP_200_OK)

class CreateBinnacles(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def create(self, request):
        user_id = request.data['user_id']
        observation = request.data['observation']      
        invoice  = request.data['id_invoice_popup']
        type  = request.data['type']
        now = datetime.now() 
        date = now.strftime("%m/%d/%Y, %H:%M:%S")

        print(type)

        if type == 'adm':            
            Binnacle.objects.create(created_at = date, observation = observation, 
                                                id_invoice_id = invoice, user_id = user_id, check_binnacle_adm = True, check_binnacle = False)
        else:
            Binnacle.objects.create(created_at = date, observation = observation, 
                                                id_invoice_id = invoice, user_id = user_id, check_binnacle = True, check_binnacle_adm = False)
        return Response("llega")

class GetListBinnaclesNumber(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def list(self, request):
        id_invoice = self.request.query_params.get('id')             
        type = self.request.query_params.get('type') 
        if(type=='st'):
            count = Binnacle.objects.filter(id_invoice=id_invoice, check_binnacle=False).count()
        else:
            count = Binnacle.objects.filter(id_invoice=id_invoice, check_binnacle_adm= False).count()
        
        return Response(count,status=status.HTTP_200_OK)

class PaymentWebhookViewSet(viewsets.ViewSet):
    authentication_classes = ()
    permission_classes = (AllowAny, )

    def create(self, request):
        """Webhook para recibir notificaciones del método de pago externo"""
        try:
            webhook_data = request.data
            print(f"✅ webhook_data: {webhook_data}")
            if not webhook_data.get('success', False):
                return Response({
                    'message': 'Webhook received but payment was not successful',
                    'result': 0
                }, status=status.HTTP_400_BAD_REQUEST)

            payment_data = webhook_data.get('data', {})
            ref_merchant = payment_data.get('ref_merchant')
            ref_checkout = payment_data.get('ref_checkout')
            payment_status = payment_data.get('estado')

            if not ref_merchant:
                return Response({
                    'message': 'Missing ref_merchant in webhook data',
                    'result': 0
                }, status=status.HTTP_400_BAD_REQUEST)

            # Buscar todas las facturas con el mismo reference
            invoices = Invoice.objects.filter(reference=ref_merchant)
            
            if not invoices.exists():
                return Response({
                    'message': f'No invoices found with reference {ref_merchant}',
                    'result': 4
                }, status=status.HTTP_404_NOT_FOUND)

            updated_invoices = []
            for invoice in invoices:
                try:
                    # Actualizar el estado según el pago
                    if payment_status == 'Aprobada' or payment_status == 'Aprobado':
                        invoice.state_id = 2
                        invoice.external_state_id = 2
                        print(f"🔄 Updating invoice {invoice.id} to state 2 (Approved)")
                    else:
                        invoice.state_id = 3
                        invoice.external_state_id = 3
                        print(f"🔄 Updating invoice {invoice.id} to state 3 (status: {payment_status})")

                    # Guardar el ref_checkout si viene en el webhook
                    if ref_checkout:
                        invoice.reference_checkout = ref_checkout
                        print(f"🔄 Saving ref_checkout {ref_checkout} for invoice {invoice.id}")

                    invoice.save()
                    print(f"✅ Successfully updated invoice {invoice.id}")
                    updated_invoices.append(invoice.id)
                    
                except Exception as e:
                    print(f"❌ Error updating invoice {invoice.id}: {str(e)}")

            return Response({
                'message': f'Updated {len(updated_invoices)} invoices successfully',
                'invoice_ids': updated_invoices,
                'reference': ref_merchant,
                'new_state': 2 if payment_status == 'Aprobada' or payment_status == 'Aprobado' else 3,
                'result': 200
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ Error processing webhook: {str(e)}")
            return Response({
                'message': f'Error processing webhook: {str(e)}',
                'result': 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)