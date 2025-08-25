from datetime import datetime
from django.core.mail.message import EmailMultiAlternatives
from requests.api import get
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


class AutenticationDataGatewayViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        data = ""
        data = {
            'api_key': settings.API_KEY_GATEWAY,
            'account_id': settings.ACCOUNT_ID_GATEWAY,
        }
        return Response(data)


class TrancsactionCheckoutViewSet(viewsets.ViewSet):
    # View to set transaction Payment Gateway.
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def create(self, request):

        # GET DATA FROM FRONTEND
        tokenPaymentGateway = request.data.get("tokenPaymentGateway")
        key = request.data.get("key")
        txnid = request.data.get("txnid")
        amount = request.data.get("amount")
        productinfo = request.data.get("productinfo")
        firstname = request.data.get("firstname")
        email = request.data.get("email")
        api_key = request.data.get("api_key")
        brand = request.data.get("brand")
        quota = request.data.get("quota")
        expiryMonth = request.data.get("expiryMonth")
        expiryYear = request.data.get("expiryYear")
        card = request.data.get("card")
        typeIdentification = request.data.get("typeIdentification")
        billingNumberIdentifier = request.data.get("billingNumberIdentifier")
        billingAddress = request.data.get("billingAddress")
        billingNames = request.data.get("billingNames")
        billingLastNames = request.data.get("billingLastNames")
        billingEmail = request.data.get("billingEmail")
        callerPhoneNumber = request.data.get("callerPhoneNumber")
        id_city = request.data.get("id_city")
        city = request.data.get("city")
        id_user_front = request.data.get("id_user_front")
        type_identifier_id = request.data.get("typeIdentification")
        products = request.data.get("products")
        
        # Handle both string and list formats for products
        if isinstance(products, str):
            products_dict = json.loads(products)
        elif isinstance(products, list):
            products_dict = products
        else:
            return Response({
                'status': False,
                'message': 'Invalid products data format',
                'result': 400
            }, status=status.HTTP_400_BAD_REQUEST)

        ##################################SET TRANSACTION ON DATA BASE########################################

        data_invoice_detail = []
        for e in products_dict:
            data_invoice_detail.append({
                'name': e["name"],
                'price': e["price"],
                'produc_code': e["produc_code"],
                'quantity': e["quantity"],
                'id_product': e["id_product"],
                'id_store': e["id_store"],
            })

        # # ORDER DICCIONARY PRODUCTS BY ID_STORE
        sort_data_invoice_detail = sorted(data_invoice_detail,
                                          key=lambda k: (k['id_store']))
        id_store = ""
        invoice_list = []
        for i in sort_data_invoice_detail:
            if i["id_store"] != id_store:
                # CREATE INVOICE ON DATA BASE
                n = Invoice.objects.create(
                    reference=txnid,
                    reference_invoice=int(round(time.time() * 1000)),
                    total_price=amount,
                    name_client=billingNames,
                    first_name_client=billingLastNames,
                    phone=callerPhoneNumber,
                    adress=billingAddress,
                    number_identifier=billingNumberIdentifier,
                    email=billingEmail,
                    city_id=id_city,
                    id_store_id=i["id_store"],
                    payment_method_id="1",
                    state_id=3,
                    type_identification_id=type_identifier_id,
                    user_id=id_user_front,
                    shipping_voucher="any.any"
                )
                id_invoice = n.id
                invoice_list.append({'id_invoice': id_invoice})

            # CREATE INVOICE DETAIL ON DATABASE
            get_price = i["price"]
            get_quant = int(i["quantity"])
            calc_price = math.trunc(int(float(get_price)))
            total = calc_price * get_quant
            InvoiceDetail.objects.create(
                id_invoice_id=id_invoice,
                id_product_id=i["id_product"],
                name_product=i["name"],
                description_product=i["name"],
                product_code=i["produc_code"],
                unit_price=i["price"],
                quantity=i["quantity"],
                total_price=total,
                reference=txnid
            )
            print(f"📦 Added product {i['name']} to invoice {id_invoice} (store {i['id_store']})")
            id_store = i["id_store"]

        # UPDATE INVOICE'S VALUES
        for iu in invoice_list:
            invoice_detail_up = InvoiceDetail.objects.filter(
                id_invoice=iu["id_invoice"])
            # GET ALL ITEMS DETAIL INVOICE PRICE AND SUM
            price_sum = 0
            for ide in invoice_detail_up:
                price_sum = price_sum + ide.total_price

            # CREATE INVOICE OBJECT
            invoice_up_tot = Invoice.objects.get(id=iu["id_invoice"])

            # GET RETE ICA
            reteica = PaymentPercentages.objects.filter(
                type_percentage_id=3).values('percentage')
            reteica = reteica[0]['percentage']
            val_reteica = (price_sum * reteica) / 100
            # #GET RETE FUENTE
            retefuente = PaymentPercentages.objects.filter(
                type_percentage_id=4).values('percentage')
            retefuente = retefuente[0]['percentage']
            val_retefuente = (price_sum * retefuente) / 100

            get_valus_store = Stores.objects.filter(
                id_store=invoice_up_tot.id_store_id)
            for p in get_valus_store:
                commision_payment = PaymentPercentages.objects.filter(
                    id=p.commission_payment_id).values('percentage')
                commision_sale = PaymentPercentages.objects.filter(
                    id=p.commission_sale_id).values('percentage')
                # GET COMISION COMPRA
                get_commision_payment = commision_payment[0]['percentage']
                val_commision_payment = (
                    price_sum * get_commision_payment) / 100
                # GET COMISION VENTA
                get_commision_sale = commision_sale[0]['percentage']
                val_commision_sale = (price_sum * get_commision_sale) / 100

            # GET IVA
            iva = PaymentPercentages.objects.filter(
                type_percentage_id=5).values('percentage')
            iva = iva[0]['percentage']
            val_percentage_commision_tax = val_commision_payment + val_commision_sale
            val_percentage_commision_tax = (
                val_percentage_commision_tax * iva) / 100

            # SET TOTAL PRICE
            invoice_up_tot.total_price = price_sum

            invoice_up_tot.percentage_sale = get_commision_sale
            invoice_up_tot.val_percentage_sale = val_commision_sale
            invoice_up_tot.percentage_commision_payment = get_commision_payment
            invoice_up_tot.val_percentage_commision_payment = val_commision_payment
            invoice_up_tot.percentage_rete_ica = reteica
            invoice_up_tot.val_percentage_rete_ica = val_reteica
            invoice_up_tot.percentage_rete_fuente = retefuente
            invoice_up_tot.val_percentage_rete_fuente = val_retefuente
            invoice_up_tot.percentage_commision_tax = iva
            invoice_up_tot.val_percentage_commision_tax = val_percentage_commision_tax

            # SET TOTAL BALCE
            invoice_up_tot.total_balance = price_sum - \
                (val_reteica + val_retefuente + val_commision_payment +
                 val_commision_sale + val_percentage_commision_tax)
            invoice_up_tot.save()

        ##################################SET TRANSACTION ON API REST PAYMENT GATEWAY########################################
        # CREATE HASH REQUIRED BY PAYMENT GATEWAY
        sign = str(key) + '|' + str(txnid) + '|' + str(amount) + '|' + str(
            productinfo) + '|' + str(firstname) + '|' + str(
                email) + '|' + '/payment/process||||||||||' + str(api_key)
        hashsha = hashlib.sha512(sign.encode('utf-8')).hexdigest()

        # CREATE JSON OBJECT TO SEND TO PAYMENT GATEWAY API
        TransactionDetail = {
            "key": key,
            "txnid": txnid,
            "amount": amount,
            "productinfo": productinfo,
            "firstname": firstname,
            "email": email,
            "hash": hashsha,
            "quota": quota,
            "brand": brand,
            "expiryMonth": expiryMonth,
            "expiryYear": expiryYear,
            "card": card,
            "typeIdentification": typeIdentification,
            "billingNumberIdentifier": billingNumberIdentifier,
            "billingAddress": billingAddress,
            "billingNames": billingNames,
            "billingLastNames": billingLastNames,
            "billingEmail": billingEmail,
            "callerPhoneNumber": callerPhoneNumber,
            "city": city
        }

        # SEND DATA TO REST API PAYMENT GATEWAY

        resp = requests.post(
            settings.API_TRANSACTION,
            json=TransactionDetail,
            headers={'Authorization': 'Bearer ' + tokenPaymentGateway})

        try:
            data = resp.text
            if not data:
                raise ValueError("Empty response from payment gateway")
            transaction_response = json.loads(data)

            obj_trx = TransactionData.objects.create(
                quot=quota,
                brand=brand,
                num_aprob=transaction_response["data"]["code"],
                cod_reply="00",
                messaje_reply=transaction_response["data"]["status"],
                reference=txnid,
                total_tx=amount
            )
            id_trx = obj_trx.id
            # UPDATE STATUS TO THE INVOICE REGISTER
            for il in invoice_list:
                invoice_up = Invoice.objects.get(id=il["id_invoice"])
                invoice_up.transaction_id = id_trx
                invoice_up.state_id = 1
                invoice_up.save()

            response = {
                'status': True,
                'num_aprob': transaction_response["data"]["code"],
                'message_reply': transaction_response["data"]["status"],
                'date': obj_trx.created_at,
                'reference': obj_trx.reference,
                'result': 200
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            if resp.text is not None:
                data_res = resp.text
                transaction_response = json.loads(data_res)
                trx_split = transaction_response["message"]
                trx_split = trx_split.split('|')
                code_response = trx_split[0]
                messaje_response = trx_split[1]

                obj_trx = TransactionData.objects.create(
                    quot=quota,
                    brand=brand,
                    num_aprob=0,
                    cod_reply=code_response,
                    messaje_reply=messaje_response,
                    reference=txnid,
                    total_tx=amount)
                id_trx = obj_trx.id

                for il in invoice_list:
                    invoice_up = Invoice.objects.get(id=il["id_invoice"])
                    invoice_up.transaction_id = id_trx
                    invoice_up.state_id = 2
                    invoice_up.save()

                data = {
                     'status': False,
                    'message': 'Fail transaction',
                    'message_reply': messaje_response,
                    'cod_reply': code_response,
                    'result': 400
                }
            else:
                for il in invoice_list:
                    invoice_up = Invoice.objects.get(id=il["id_invoice"])
                    invoice_up.transaction_id = id_trx
                    invoice_up.state_id = 2
                    invoice_up.save()
                data = {
                    'status': False,
                    'message': 'Fail transaction',
                    'result': 500
                }
            return Response(data, status=status.HTTP_200_OK)

class TrancsactionCoreViewSet(viewsets.ViewSet):
    # View to set transaction Payment Gateway by Core Transaction.
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def create(self, request):
            # GET DATA FROM FRONTEND
            txnid = request.data.get("txnid")
            billingNames = request.data.get("billingNames")
            billingLastNames = request.data.get("billingLastNames")
            id_user_front = request.data.get("id_user_front")
            type_identifier_id = request.data.get("typeIdentification") 
            identificationNumber = request.data.get("identificationNumber")
            total = request.data.get("total")
            typeTax = request.data.get("typeTax")
            tax = request.data.get("tax")
            address = request.data.get("address")
            department = request.data.get("department")
            city = request.data.get("city")
            id_city = request.data.get("id_city")
            email = request.data.get("email")
            phone = request.data.get("phone")
            celphone = request.data.get("celphone")
            products = request.data.get("products")
            
            # Handle both string and list formats for products
            if isinstance(products, str):
                products_dict = json.loads(products)
            elif isinstance(products, list):
                products_dict = products
            else:
                return Response({
                    'status': False,
                    'message': 'Invalid products data format',
                    'result': 400
                }, status=status.HTTP_400_BAD_REQUEST)


            data_invoice_detail = []
            for e in products_dict:
                data_invoice_detail.append({
                'name': e["name"],
                'price': e["price"],
                'produc_code': e["produc_code"],
                'quantity': e["quantity"],
                'id_product': e["id_product"],
                'id_store': e["id_store"],
            })

            # # ORDER DICCIONARY PRODUCTS BY ID_STORE
            sort_data_invoice_detail = sorted(data_invoice_detail,
                                        key=lambda k: (k['id_store']))

            id_store = ""
            invoice_list = []
            id_store_id_tx = ""

            for i in sort_data_invoice_detail:
                print(f"Processing product: {i['name']} for store: {i['id_store']}, current id_store: {id_store}")
                
                # Si es una nueva tienda, crear nueva factura
                if i["id_store"] != id_store:
                    # CREATE INVOICE ON DATA BASE
                    n = Invoice.objects.create(
                        reference=txnid,
                        reference_invoice=int(round(time.time() * 1000)),
                        # total_price=total,
                        name_client=billingNames,
                        first_name_client=billingLastNames,
                        phone=celphone,
                        adress=address,
                        number_identifier=identificationNumber,
                        email=email,
                        city_id=id_city,
                        id_store_id=i["id_store"],
                        payment_method_id="1",
                        state_id=3,
                        type_identification_id=type_identifier_id,
                        user_id=id_user_front,
                        shipping_voucher="any.any",
                        type_service_id=1
                    )
                    id_invoice = n.id
                    invoice_list.append({'id_invoice': id_invoice})
                    id_store_id_tx = i["id_store"]
                    id_store = i["id_store"]  # Actualizar id_store inmediatamente
                    
                # CREATE INVOICE DETAIL ON DATABASE (solo para productos de esta tienda)
                get_price = i["price"]
                get_quant = int(i["quantity"])
                calc_price = math.trunc(int(float(get_price)))
                total = calc_price * get_quant

                InvoiceDetail.objects.create(
                    id_invoice_id=id_invoice,
                    id_product_id=i["id_product"],
                    name_product=i["name"],
                    description_product=i["name"],
                    product_code=i["produc_code"],
                    unit_price=i["price"],
                    quantity=i["quantity"],
                    total_price=total,
                    reference=txnid
                )
            
            # UPDATE INVOICE'S VALUES
            for iu in invoice_list:
                invoice_detail_up = InvoiceDetail.objects.filter(
                    id_invoice=iu["id_invoice"])
                # GET ALL ITEMS DETAIL INVOICE PRICE AND SUM
                price_sum = 0

                # Primero sumar todos los productos de esta factura
                for ide in invoice_detail_up:
                    price_sum = price_sum + ide.total_price

                # CREATE INVOICE OBJECT (FUERA del bucle de productos)
                invoice_up_tot = Invoice.objects.get(id=iu["id_invoice"])

                # GET RETE ICA
                reteica = PaymentPercentages.objects.filter(
                    type_percentage_id=3).values('percentage')
                reteica = reteica[0]['percentage']
                val_reteica = (price_sum * reteica) / 100

                # #GET RETE FUENTE
                retefuente = PaymentPercentages.objects.filter(
                    type_percentage_id=4).values('percentage')
                retefuente = retefuente[0]['percentage']
                val_retefuente = (price_sum * retefuente) / 100

                get_valus_store = Stores.objects.filter(
                    id_store=invoice_up_tot.id_store_id)

                for p in get_valus_store:
                    commision_payment = PaymentPercentages.objects.filter(
                        id=p.commission_payment_id).values('percentage')
                    commision_sale = PaymentPercentages.objects.filter(
                        id=p.commission_sale_id).values('percentage')
                    # GET COMISION COMPRA
                    get_commision_payment = commision_payment[0]['percentage']
                    val_commision_payment = (
                        price_sum * get_commision_payment) / 100
                    # GET COMISION VENTA
                    get_commision_sale = commision_sale[0]['percentage']
                    val_commision_sale = (
                        price_sum * get_commision_sale) / 100

                # GET IVA
                iva = PaymentPercentages.objects.filter(
                    type_percentage_id=5).values('percentage')
                iva = iva[0]['percentage']
                val_percentage_commision_tax = val_commision_payment + val_commision_sale
                val_percentage_commision_tax = (
                    val_percentage_commision_tax * iva) / 100

                # SET TOTAL PRICE
                invoice_up_tot.total_price = price_sum
                invoice_up_tot.percentage_sale = get_commision_sale
                invoice_up_tot.val_percentage_sale = val_commision_sale
                invoice_up_tot.percentage_commision_payment = get_commision_payment
                invoice_up_tot.val_percentage_commision_payment = val_commision_payment
                invoice_up_tot.percentage_rete_ica = reteica
                invoice_up_tot.val_percentage_rete_ica = val_reteica
                invoice_up_tot.percentage_rete_fuente = retefuente
                invoice_up_tot.val_percentage_rete_fuente = val_retefuente
                invoice_up_tot.percentage_commision_tax = iva
                invoice_up_tot.val_percentage_commision_tax = val_percentage_commision_tax

                # SET TOTAL BALCE
                invoice_up_tot.total_balance = price_sum - \
                    (val_reteica + val_retefuente + val_commision_payment +
                     val_commision_sale + val_percentage_commision_tax)
                invoice_up_tot.save()
                
                print(f"💰 Updated invoice {iu['id_invoice']} with total: {price_sum}")

            print(f"📋 Invoice list contains {len(invoice_list)} invoices: {invoice_list}")
            
            # UPDATE STATUS TO THE INVOICE REGISTER
            print(f"🔧 Starting to update {len(invoice_list)} invoices to state 1")
            for il in invoice_list:
                try:
                    print(f"🔄 Updating invoice {il['id_invoice']} to state 1")
                    invoice_up = Invoice.objects.get(id=il["id_invoice"])
                    invoice_up.state_id = 1
                    invoice_up.external_state_id = 1
                    invoice_up.save()
                    print(f"✅ Successfully updated invoice {il['id_invoice']}")
                except Exception as e:
                    print(f"❌ Error updating invoice {il['id_invoice']}: {str(e)}")
            
            print("🎉 All invoice updates completed")

            print("🚀 Preparing response...")
            response = {
                'status': True,
                'result': 200
            }
            print("✅ Returning successful response")
            return Response(response, status=status.HTTP_200_OK)



class GetAllTransactionsViewSet(viewsets.ViewSet):
    serializer_class = TransactionDataSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        data = []
        sql = "select trd.*, at2.name_state from api_transactiondata trd left join api_transactionstate at2 on at2.id = trd.state_id order by trd.id desc"
        # for p in TransactionData.objects.all().order_by('-id'):
        for p in TransactionData.objects.raw(sql):
            
            invoiceObject = Invoice.objects.filter(
                    transaction_id=p.id)
            ValidInvoiceOnTransfer = 0
            for a in invoiceObject:
                if a.state_id == 8:
                    ValidInvoiceOnTransfer = 1

            data.append({
                'id': p.id,
                'created_at': p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'quot': p.quot,
                'brand': p.brand,
                'num_aprob': p.num_aprob,
                'cod_reply': p.cod_reply,
                'messaje_reply': p.messaje_reply,
                'reference': p.reference,
                'total_tx': p.total_tx,
                'num_recibo': p.num_recibo,
                'state': p.state_id,
                'name_state': p.name_state,
                'ValidInvoiceOnTransfer': ValidInvoiceOnTransfer
            })
        return Response(data)


class GetTransactionsByStoreViewSet(viewsets.ViewSet):
    serializer_class = TransactionDataSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        id_store = self.request.query_params.get('id_store', None)
        data = []
        for p in TransactionData.objects.filter(tag_store=id_store).order_by('-id'):
            data.append({
                'id': p.id,
                'created_at': p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'quot': p.quot,
                'brand': p.brand,
                'num_aprob': p.num_aprob,
                'num_recibo': p.num_recibo,
                'cod_reply': p.cod_reply,
                'messaje_reply': p.messaje_reply,
                'reference': p.reference,
                'total_tx': p.total_tx,
                'state': p.state_id,
                'name_state': p.state.name_state,
                'tag_first_name' : p.tag_first_name,
                'tag_last_name' : p.tag_last_name,
                'tag_type_identification' : p.tag_type_identification.type_identifier,
                'tag_number_identification' : p.tag_number_identification,
                'tag_email' : p.tag_email, 
                'tag_cellphone' : p.tag_cellphone,
                'tag_desc_selling' : p.tag_desc_selling,                
            })
        return Response(data)


class GetTransactionsByIdViewSet(viewsets.ViewSet):
    serializer_class = TransactionDataSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        idTransaction = self.request.query_params.get('id', None)
        data = []

        transactionObject = TransactionData.objects.get(id=idTransaction)
        
        data = {
            'id': transactionObject.id,
            'created_at': transactionObject.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'quot': transactionObject.quot,
            'brand': transactionObject.brand,
            'num_aprob': transactionObject.num_aprob,
            'num_recibo': transactionObject.num_recibo,
            'cod_reply': transactionObject.cod_reply,
            'messaje_reply': transactionObject.messaje_reply,
            'reference': transactionObject.reference,
            'total_tx': transactionObject.total_tx,
            'state': transactionObject.state_id,
            'name_state': transactionObject.state.name_state,
            'tag_first_name' : transactionObject.tag_first_name,
            'tag_last_name' : transactionObject.tag_last_name,
            'tag_type_identification' : transactionObject.tag_type_identification.type_identifier,
            'tag_number_identification' : transactionObject.tag_number_identification,
            'tag_email' : transactionObject.tag_email, 
            'tag_cellphone' : transactionObject.tag_cellphone,
            'tag_desc_selling' : transactionObject.tag_desc_selling,               
        }
        return Response(data)


class CancelTransactionViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def update(self, request, pk=None):
        # try:
        id_tx_obj = TransactionData.objects.get(id=pk)

        cancelTransactionJsonObj = {
            "SoapCertificate": id_tx_obj.cuc.soapcertificate,
            "soapUrl": id_tx_obj.cuc.soapurl,
            "soapPassphrase": id_tx_obj.cuc.soappassphrase,
            "soapUser": id_tx_obj.cuc.soapuser,
            "soapPassword": id_tx_obj.cuc.soappassword,
            "cuc": id_tx_obj.cuc.cuc,
            "terminal": id_tx_obj.cuc.terminal,
            "NumReciboDev": id_tx_obj.num_recibo
        }

        resp = requests.post(
            settings.API_TRANSACTION+'credibanco_cancel',
            json=cancelTransactionJsonObj,
            headers={'AccountXToken': 'accountxtoken', 'AccountXKey': 'accountxkey'})

        data = resp.text
        transaction_response = json.loads(data)

        NumRecibo = transaction_response["data"]["NumRecibo"]
        NumAutorizacion = transaction_response["data"]["NumAutorizacion"]
        MsgResp = transaction_response["data"]["MsgResp"]
        date = transaction_response["data"]["date"]

        data = ""
        if transaction_response["data"]["MsgResp"] == "00":
            # TRANSACTION IS CANCEL BY CHANEL TRANSACTION

            # TRANSACTION CANCEL IS REGISTER ON DB
            obj_trx_cancel = TransactionCancelData.objects.create(
                transaction_id=TransactionData.objects.get(id=pk),
                num_aprob=NumAutorizacion,
                num_recibo=NumRecibo,
                messaje_reply=MsgResp,
                date_chanel_tx=date
            )

            id_cancel_trx = obj_trx_cancel.id
            # UPDATE TRANSACCION STATE AND REGISTER AS CANCEL
            tx_obj = TransactionData.objects.get(id=pk)
            tx_obj.state_id = 2
            tx_obj.save()

            # UPDATE INVOICE'S STATUS
            inv_obj = Invoice.objects.filter(reference=id_tx_obj.reference)
            for inv in inv_obj:
                up_inv_sta = Invoice.objects.get(id=inv.id)
                up_inv_sta.state_id = 7
                up_inv_sta.external_state_id = 4
                up_inv_sta.canceled = True
                up_inv_sta.save()

                # if inv.state_id == 8:
                #     canceledInTransfer = Invoice.objects.get(id=inv.id)
                #     canceledInTransfer.canceled_in_transfer = True
                #     canceledInTransfer.save()

            data = {
                'num_recibo': NumRecibo,
                'num_autorizacion': NumAutorizacion,
                'msgresp': MsgResp,
                'date': date,
            }

            response = {
                        'data': data,
                        'message': 'Transaction cancel correctly',
                        'result': 200
                    }
            return Response(response, status=status.HTTP_200_OK)

        else:
            # TRANSACTION CANCER IS REGISTER ON DB
            obj_trx_cancel = TransactionCancelData.objects.create(
                transaction_id=TransactionData.objects.get(id=pk),
                num_aprob=NumAutorizacion,
                num_recibo=NumRecibo,
                messaje_reply=MsgResp,
                date_chanel_tx=date
            )

            data = {
                'num_recibo': NumRecibo,
                'num_autorizacion': NumAutorizacion,
                'msgresp': MsgResp,
                'date': date,
            }
            response = {
                        'data': data,
                        'message': 'Server ok but Fail transaccion',
                        'result': 200
                    }
            return Response(response, status=status.HTTP_200_OK)
        # except:
        #     response = {
        #             'message': 'No cancel transaction, server fail verify core transaction or chanel transaction',
        #             'result': 400
        #         }
        #     return Response(response, status=status.HTTP_400_BAD_REQUEST)



class ContraTransactionViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def update(self, request, pk=None):        
        id_tx_obj = TransactionData.objects.get(id=pk)
        # UPDATE TRANSACCION STATE AND REGISTER AS CONTRA
        tx_obj = TransactionData.objects.get(id=pk)
        tx_obj.state_id = 5
        tx_obj.save()

        inv_obj = Invoice.objects.filter(reference=id_tx_obj.reference)
        for inv in inv_obj:
            up_inv_sta = Invoice.objects.get(id=inv.id)
            up_inv_sta.state_id = 11
            up_inv_sta.external_state_id = 6
            up_inv_sta.contra = True
            up_inv_sta.save()
        
        response = {
                    'message': 'Transaction cancel correctly',
                    'result': 200
                }
        return Response(response, status=status.HTTP_200_OK)



class sendCustomerStoreEmailViewSet(viewsets.ViewSet):
    authentication_classes = ()
    permission_classes = ()

    def create(self, request):
        try:
            template = get_template('mails/approved_transaction.html')
            user_mail = request.data.get("email")
            reference = request.data.get("txnid")
            subject = 'Has comprado '
            subtotal = 0
            total = 0

            invoice_data = Invoice.objects.filter(reference=reference)
            data = []
            for p in invoice_data:
                name_client = p.name_client
                last_name_client = p.first_name_client
                celphone = p.phone
                number_identifier = p.number_identifier
                adress = p.adress
                city = p.city

                get_data_invdetail = InvoiceDetail.objects.filter(
                    id_invoice=p.id)
                get_data_transaction = TransactionData.objects.filter(
                    reference=reference)

                for i in get_data_invdetail:
                    subject += i.name_product + ' '
                    image = settings.AWS_URL_BUCKET_DOCS + \
                        str(i.id_product.image)
                    total_price = int(i.quantity) * float(i.unit_price)
                    subtotal += total_price
                    total += total_price

                    data.append({
                        'quantity': i.quantity,
                        'unit_price': i.unit_price,
                        'name_product': i.name_product,
                        'image': image,
                        'total_price': total_price,
                    })
                    for d in get_data_transaction:
                        num_aprob = d.num_aprob
                        message_reply = d.messaje_reply
                        cod_reply = d.cod_reply
                        date = str(d.created_at)
                        date_format = datetime.strptime(
                            date[0:19], '%Y-%m-%d %H:%M:%S')
                        get_data_transaction_state = TransactionState.objects.filter(
                            id=d.state_id)
                        for st in get_data_transaction_state:
                            estado = st.name_state
            subject += '- Referencia No. '+str(reference)
            content = template.render({
                        'user_mail': user_mail,
                        'data': data,
                        'subtotal': subtotal,
                        'total': total,
                        'reference': reference,
                        'name_client': name_client,
                        'celphone': celphone,
                        'last_name_client': last_name_client,
                        'number_identifier': number_identifier,
                        'adress': adress,
                        'city': city,
                        'cod_reply': cod_reply,
                        'num_aprob': num_aprob,
                        'message_reply': message_reply,
                        'date': date_format,
                        'estado': estado,
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
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {
                'message': 'Can´t send email  '
            }
            return Response(response,
                            status=status.HTTP_400_BAD_REQUEST)


class sendSellerEmailViewSet(viewsets.ViewSet):
    authentication_classes = ()
    permission_classes = ()

    def create(self, request):
        # try:
            reference = request.data.get("txnid")
            subtotal = 0
            total = 0
            total_price = 0
            invoice_data = Invoice.objects.filter(reference=reference)
            try:
                get_data_transaction = TransactionData.objects.get(
                    reference=reference)
            except TransactionData.DoesNotExist:
                response = {'message': 'Transaction data not found for reference: ' + str(reference), 'result': 400}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            # import pdb; pdb.set_trace()
            for p in invoice_data:
                name_client = p.name_client
                user_mail = p.email
                last_name_client = p.first_name_client
                celphone = p.phone
                number_identifier = p.number_identifier
                adress = p.adress
                city = p.city
                reference_invoice = p.reference_invoice
                store_email = p.id_store.email

                get_data_invdetail = InvoiceDetail.objects.filter(
                    id_invoice=p.id)
                data_invoice_detail = []
                total = 0
                for i in get_data_invdetail:
                    name_product = i.name_product
                    image = settings.AWS_URL_BUCKET_DOCS + \
                        str(i.id_product.image)
                    total_price = int(i.quantity) * float(i.unit_price)
                    id_store_d = i.id_invoice.id_store.id_store
                    unit_price = i.unit_price
                    quantity = i.quantity
                    total = total + total_price

                    data_invoice_detail.append({
                        'image': image,
                        'total_price': total_price,
                        'subtotal': subtotal,
                        'id_store_d': id_store_d,
                        'name_product': name_product,
                        'quantity': quantity,
                        'unit_price': unit_price,
                    })

                template = get_template('mails/sold_product_information.html')
                content = template.render({
                                'reference': reference_invoice,
                                'data_invoice_detail': data_invoice_detail,
                                'total': total,
                                'name_client': name_client+last_name_client,
                                'user_mail': user_mail,
                                'celphone': celphone,
                                'number_identifier': number_identifier,
                                'adress': adress,
                                'city': city,
                                'cod_reply': get_data_transaction.cod_reply,
                                'num_aprob': get_data_transaction.num_aprob,
                                'date': get_data_transaction.created_at,
                                'state': get_data_transaction.state.name_state,
                                'reference_tx': reference,
                            })

                subject = 'Has recibido un nuevo pedido con No. ' + \
                    str(reference_invoice)
                message = EmailMultiAlternatives(subject,  # Titulo
                                '',
                                    settings.EMAIL_HOST_USER,  # Remitente
                                    to=[
                                        store_email
                                    ])  # Destinatario
                message.attach_alternative(content, 'text/html')
                message.send()
            response = {'messaje': 'Send email', 'result': 200}
            return Response(response, status=status.HTTP_200_OK)
        # except:
        #     response = {
        #         'message': 'Can´t send email  '
        #     }
        #     return Response(response,
        #                     status=status.HTTP_400_BAD_REQUEST)


class sendEmailRejectionTransactionCustomerViewSet (viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()

    def create(self, request):
        try:
            template = get_template('mails/rejection_transaction.html')
            user_mail = request.data.get("email")
            reference = request.data.get("txnid")
            subject = 'Transacción rechazada '
            subtotal = 0
            total = 0

            invoice_data = Invoice.objects.filter(reference=reference)
            data = []
            for p in invoice_data:
                name_client = p.name_client
                last_name_client = p.first_name_client
                celphone = p.phone
                number_identifier = p.number_identifier
                adress = p.adress
                city = p.city

                get_data_invdetail = InvoiceDetail.objects.filter(
                    id_invoice=p.id)
                get_data_transaction = TransactionData.objects.filter(
                    reference=reference)

                for i in get_data_invdetail:
                    image = settings.AWS_URL_BUCKET_DOCS + \
                        str(i.id_product.image)
                    total_price = int(i.quantity) * float(i.unit_price)
                    subtotal += total_price
                    total += total_price

                    data.append({
                        'quantity': i.quantity,
                        'unit_price': i.unit_price,
                        'name_product': i.name_product,
                        'image': image,
                        'total_price': total_price,
                    })
                    for d in get_data_transaction:
                        num_aprob = d.num_aprob
                        message_reply = d.messaje_reply
                        cod_reply = d.cod_reply
                        date = str(d.created_at)
                        date_format = datetime.strptime(
                            date[0:19], '%Y-%m-%d %H:%M:%S')
                        get_data_transaction_state = TransactionState.objects.filter(
                            id=d.state_id)
                        for st in get_data_transaction_state:
                            estado = st.name_state
            print(estado)
            content = template.render({
                        'user_mail': user_mail,
                        'data': data,
                        'subtotal': subtotal,
                        'total': total,
                        'reference': reference,
                        'name_client': name_client,
                        'celphone': celphone,
                        'last_name_client': last_name_client,
                        'number_identifier': number_identifier,
                        'adress': adress,
                        'city': city,
                        'cod_reply': cod_reply,
                        'num_aprob': num_aprob,
                        'message_reply': message_reply,
                        'date': date_format,
                        'estado': estado,
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
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {
                'message': 'Can´t send email  '
            }
            return Response(response,
                            status=status.HTTP_400_BAD_REQUEST)

from django.http import JsonResponse

class SetTransaction(object):

    def __init__(self):
        """Constructor de clase Transaccion"""
        
    def SetTransactionAssisted(objectTransaction):

        try:
            typeTax = 1
            tax = 0
            address = "na"
            department = "na"
            city = "na"
            id_city = 1
            txnid = objectTransaction["txnid"] 
            cardNumber = objectTransaction["cardNumber"].replace(' ','')  
            expiryMonth = objectTransaction["expiryMonth"]
            expiryYear = objectTransaction["expiryYear"]  
            securityCode = objectTransaction["securityCode"] 
            brand = objectTransaction["brand"]
            quota = objectTransaction["quota"]
            billingNames = objectTransaction["billingNames"]
            billingLastNames = objectTransaction["billingLastNames"]
            webProductsReference = objectTransaction["webProductsReference"]
            typeIdentification = objectTransaction["typeIdentification"]
            identificationNumber = objectTransaction["identificationNumber"]
            phone = objectTransaction["tag_cellphone"]
            celphone = objectTransaction["tag_cellphone"]
            total = objectTransaction["total_tx"]                                    
            email = objectTransaction["tag_email"]
            idTransactionData = objectTransaction["idTransactionData"]
            #import pdb; pdb.set_trace()
            if brand == 'visa':
                franc = '90'
            elif brand == 'amex':
                franc = '30'
            elif brand == 'mastercard':
                franc = '91'
            elif brand == 'diners':
                franc = '34'

            transactionDataObj = TransactionData.objects.get(id=idTransactionData)
            store_id = transactionDataObj.tag_store_id
            storeData = Stores.objects.get(id_store=store_id)

            # CREATE JSON OBJECT TO SEND TO PAYMENT GATEWAY API
            TransactionDetail = {
                "SoapCertificate": storeData.cuc.soapcertificate,
                "soapUrl": storeData.cuc.soapurl,
                "soapPassphrase": storeData.cuc.soappassphrase,
                "soapUser": storeData.cuc.soapuser,
                "soapPassword": storeData.cuc.soappassword,
                "cuc": storeData.cuc.cuc,
                "terminal": storeData.cuc.terminal,
                "tipoTerminal": "1",
                "idTerminal": "1",
                "idAdquiriente": "1",
                "webProductsReference": webProductsReference,
                "modoCapturaPAN": "1",
                "capacidadPIN": "1",
                "typeIdentification": typeIdentification,
                "identificationNumber": "1",
                "brand": "1",
                "cardNumber": cardNumber,
                "expiryMonth": expiryMonth,
                "expiryYear": expiryYear,
                "securityCode": securityCode,
                "quota": quota,
                "total": total,
                "typeTax": typeTax,
                "tax": tax,
                "address": address,
                "department": department,
                "city": city,
                "email": email,
                "phone": phone,
                "celphone": celphone,
                "franquicia": franc
            }

            print("############################################################################")
            print("############################################################################")
            print("############################################################################")
            print("############################################################################")
            print("############################################################################")
            print("############################################################################")
            print(TransactionDetail)

            # SEND DATA TO REST API PAYMENT GATEWAY
            resp = requests.post(
                settings.API_TRANSACTION+'credibanco',
                json=TransactionDetail,
                headers={'AccountXToken': 'accountxtoken', 'AccountXKey': 'accountxkey'})

            data = resp.text

            print("############################################################################")
            print(data)
            transaction_response = json.loads(data)

            if (transaction_response["data"]["MsgResp"]=='00'):
                statate = 1
            else:
                statate = 3

            transactionDataObj = TransactionData.objects.get(id=idTransactionData)
            transactionDataObj.num_aprob = transaction_response["data"]["NumAutorizacion"]
            transactionDataObj.cod_reply=transaction_response["data"]["MsgResp"]
            transactionDataObj.messaje_reply=transaction_response["data"]["MsgResp"]
            transactionDataObj.num_recibo=transaction_response["data"]["NumRecibo"]
            transactionDataObj.state_id=statate
            transactionDataObj.cuc_id=storeData.cuc.id        
            transactionDataObj.save()

            transaction_txinf = TrxInf.objects.create(
                field=cardNumber,
                tx_id=idTransactionData,
            )
            transaction_txinf.save()
            
            response = {
                'message': 'Transaction execute ',
                'codreply': transaction_response["data"]["MsgResp"],
                'status': 200,
            }
            return response;

        except:
            response = {
                'message': 'Transaction dont execute  ',
                'status': 400,
            }
            return response;

class ExportableTransactionViewSet (viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def create(self, request):

        initial_date = request.data['initial_date']
        finish_date = request.data['finish_date']
        
        data = []
        sql = """select trd.*, ty.type_identifier, est.name_state, txin.field, st.name_store 
                from api_transactiondata trd 
                left join api_typeidentification ty on ty.id = trd.tag_type_identification_id
                left join api_transactionstate est on est.id = trd.state_id                
                left join api_trxinf txin on txin.tx_id = trd.id
                left join api_stores st on st.id_store = trd.tag_store_id
                where trd.created_at between '{0}' and '{1}'  
                order by trd.id desc
                """.format(initial_date,finish_date)
                
        for p in TransactionData.objects.raw(sql):
            first_name = str(p.tag_first_name)
            last_name = str(p.tag_last_name)
            name = first_name+ ' '+last_name
            getFieldNumUltimate = ""
            getFieldNumFirst = ""
            if p.field != None:
                getFieldNumUltimate = p.field[-4:]
                getFieldNumFirst = p.field[:5]
                
            data.append({
                'Tienda': p.name_store,
                'Fecha Creacion': p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'Cuotas': p.quot,
                'Franquicia': p.brand,
                'Num Aprob': p.num_aprob,
                'Num Recibo': p.num_recibo,
                'Cod Respuesta': p.cod_reply,
                'Mensaje Respu': p.messaje_reply,
                'Referencia': p.reference,
                'Total': p.total_tx,    
                'Estado': p.name_state,
                'Nombre' : name,
                'Tipo de indentiticacion' : p.type_identifier,
                'Numero Identificacion' : p.tag_number_identification,
                'Email' : p.tag_email, 
                'Numero Contacto' : p.tag_cellphone,
                'Descripcion venta' : p.tag_desc_selling,
                'Num tarj' : getFieldNumUltimate,                
                'Bin' : getFieldNumFirst
            })
        return Response(data)
    


