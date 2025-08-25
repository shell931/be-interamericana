from rest_framework import viewsets, status
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from ..models import *
from ..serializers import UserSerializer, GroupSerializer, \
    MenuSerializer, CreateUserSerializer, StoresSerializer, \
    DepartmentsSerializer, CitiesSerializer, ProductsSerializer,\
    CategoriesSerializer, ImagesSerializer, ProductsFrontStoreSerializer, \
    AdminProductSerializer, LocationClientSerializer, LocationClientByUserSerializer, SubCategoriesSerializer, TypeIdentificationSerializer, InvoiceDetalSerializer, InvoiceSerializer, BankAccountsSerializer
from django.contrib.auth.models import Group
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from itertools import chain
from django.db import connection
from datetime import datetime
import json
import collections
import requests
import os
from django.core.mail.message import EmailMultiAlternatives
import boto3




class StoreNavStoreViewSet(viewsets.ViewSet):
    serializer_class = StoresSerializer
    authentication_classes = ()
    permission_classes = ()

    def list(self, request):
        id_store = self.request.query_params.get('id_store', None)
        id_category = self.request.query_params.get('id_category', None)
        data = []        
        if id_store:
            sql =  "select * from api_stores where id_store = "+str(id_store)
        elif id_category: 
            if id_category == "null":
                sql =  "select * from api_stores where state_store = true"
            else:
                sql =  "select * from api_stores where state_store = true and storecategories_id = "+str(id_category)                
        else:
            sql =  "select * from api_stores where state_store = true and logo_store = '1' ORDER BY RANDOM ();"
            

        for p in Stores.objects.raw(sql):
            data.append({
                "id_store": p.id_store,
                "created_at": p.created_at,
                "name_store": p.name_store,
                "address": p.address,
                "telephone": p.telephone,
                "email": p.email,
                "number_identifier": p.number_identifier,
                "manager":  p.manager,
                "state_store": p.state_store,
                "city": p.city_id,
                "logo_store": p.logo_store,
                "description": p.description,
                "storecategories": p.storecategories_id,
                "logo_store_up": str(p.logo_store_up),
            })
        return Response(data)





class StoresViewSet(viewsets.ModelViewSet):
    queryset = Stores.objects.all().order_by('-id_store')
    serializer_class = StoresSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    @action(detail=True, methods=['POST', 'DELETE'])
    def action_store(self, request, pk=None):
        if request.method == 'POST':
            """http://127.0.0.1:8000/api/store/1/action_store /"""
            if 'logo_store' in request.data:
                logo = request.data['logo_store']
                try:
                    store = Stores.objects.get(id_store=pk)
                    store.logo_store = logo
                    store.save()
                    serializer = StoresSerializer(store, many=False)
                    response = {
                        'message': 'Logo update',
                        'result': serializer.data
                    }
                    return Response(response, status=status.HTTP_200_OK)
                except:
                    """rating = Rating.objects.create(user=user, movie=movie, stars=stars)
                    serializer = RatingSerializer(rating, many=False)
                    response = {'message': 'Rating crated',
                        'result': serializer.data}
                    return Response(response, status=status.HTTP_200_OK)"""
                    response = {
                        'message': 'you need to provide image name ....'
                    }
                    return Response(response,
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                response = {'message': 'you need to provide image name'}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            """ try:
                 product = Products.objects.get(id_product=pk)
                 product.delete()
                 response = {
                     'message': 'Product delete correctly', 'result': 200}
                 return Response(response, status=status.HTTP_200_OK)
             except:
                 response = {'message': 'No find product', 'result': 400}
                 return Response(response, status=status.HTTP_400_BAD_REQUEST)"""


class StoreUpdateViewSet(viewsets.ModelViewSet):
    queryset = Stores.objects.all()
    serializer_class = StoresSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    @action(detail=True, methods=['PUT'])
    def action_store(self, request, pk=None):
        if request.method == 'PUT':
            # """http://127.0.0.1:8000/api/store/1/action_store /"""
            if 'logo_store' in request.data:
                # IMAGES LOGO UPDATE
                logo = request.data['logo_store']
                description = request.data['description']
                address = request.data['address']
                telephone = request.data['telephone']
                email = request.data['email']
                city = request.data['city']
                storecategories = request.data['storecategories']
                manager = request.data['manager']
                
                try:
                    store = Stores.objects.get(id_store=pk)
                    store.logo_store = logo
                    store.description = description
                    store.address = address
                    store.telephone = telephone
                    store.email = email
                    store.city_id = city                
                    store.rel_storecategories=StoreCategories.objects.get(
                        id=storecategories),
                    store.manager = manager
                    store.save()
                    serializer = StoresSerializer(store, many=False)
                    response = {
                        'message': 'Logo update',
                        'result': serializer.data
                    }
                    return Response(response, status=status.HTTP_200_OK)
                except:
                    response = {
                        'message': 'you need to provide image name ....'
                    }
                    return Response(response,
                                    status=status.HTTP_400_BAD_REQUEST)
            elif 'state_store' in request.data:
                # UPDATE STORE STATE
                try:
                    state_store = request.data['state_store']
                    store = Stores.objects.get(id_store=pk)
                    store.state_store = state_store
                    store.save()
                    serializer = StoresSerializer(store, many=False)
                    response = {
                        'message': 'State update!',
                        'result': serializer.data
                    }
                    return Response(response, status=status.HTTP_200_OK)
                except:
                    response = {'message': 'you need to provide state'}
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
                


class StoreCompleteData(viewsets.ViewSet):
    serializer_class = StoresSerializer
    authentication_classes = ()
    permission_classes = ()

    def list(self, request):
        id_store = self.request.query_params.get('id_store', None)
        data = ""
        if id_store is not None:
            sql = 'select st.*,ciu.city as cit,dep.id_departament,dep.departament, stcat.name_category from api_stores st ' \
                  'left join api_cities ciu on ciu.id_city = st.city_id  ' \
                  'left join api_departments dep on dep.id_departament = ciu.id_departament_id ' \
                'left join api_storecategories stcat on stcat.id = st.storecategories_id ' \
                  'where st.id_store = '+str(id_store)

            for p in Stores.objects.raw(sql):
                data = {
                    'id_store': p.id_store,
                    'name_store': p.name_store,
                    'address': p.address,
                    'telephone': p.telephone,
                    'email': p.email,
                    'number_identifier': p.number_identifier,
                    'manager': p.manager,
                    'state_store': p.state_store,
                    'city_id': p.city_id,
                    'logo_store': p.logo_store,
                    'logo_store_up': str(p.logo_store_up),
                    'description': p.description,
                    'city': p.cit,
                    'id_departament': p.id_departament,
                    'departament': p.departament,
                    'storecategories': p.storecategories_id,
                    'storecategories_description': p.name_category,
                    'commission_payment_id': p.commission_payment_id,
                    'commission_sale_id': p.commission_sale_id,
                    'cuc_id': p.cuc_id
                }
        return Response(data)


class StoreByCategoryData(viewsets.ViewSet):
    serializer_class = StoresSerializer
    authentication_classes = ()
    permission_classes = ()

    def list(self, request):
        # id_store = self.request.query_params.get('id_store', None)
        storecategories_id = self.request.query_params.get(
            'storecategories_id', None)

        data = []
        if storecategories_id is not None:
            sql = "select st.*,ciu.city as cit,dep.id_departament,dep.departament from api_stores st " \
                  "left join api_cities ciu on ciu.id_city = st.city_id  " \
                  "left join api_departments dep on dep.id_departament = ciu.id_departament_id " \
                  "where st.storecategories_id = " + \
                str(storecategories_id)+" and st.state_store = true and st.logo_store_up <> '' and st.logo_store <> ''"
            for p in Stores.objects.raw(sql):
                data.append({
                    'id_store': p.id_store,
                    'name_store': p.name_store,
                    'address': p.address,
                    'telephone': p.telephone,
                    'email': p.email,
                    'number_identifier': p.number_identifier,
                    'manager': p.manager,
                    'state_store': p.state_store,
                    'city_id': p.city_id,
                    'logo_store': p.logo_store,
                    'logo_store_up': str(p.logo_store_up),
                    'description': p.description,
                    'city': p.cit,
                    'id_departament': p.id_departament,
                    'departament': p.departament,
                    'storecategories': p.storecategories_id
                })
        return Response(data)


class MembershipRequest(viewsets.ViewSet):
    """
    View to set store.
    """
    authentication_classes = ()
    permission_classes = ()

    def create(self, request):
        # GET DATA FROM FRONTEND
        # try:
        name_store = request.data.get("name_store")
        name_legal = request.data.get("name_legal")
        address = request.data.get("address")
        telephone = request.data.get("telephone")
        mobile = request.data.get("mobile")
        email = request.data.get("email")
        number_identifier = request.data.get("number_identifier")
        manager = request.data.get("manager")
        state_store = request.data.get("state_store")
        city = request.data.get("city")
        description = request.data.get("description")
        storecategories = request.data.get("storecategories")
        postal_code = request.data.get("postal_code")
        societytype = request.data.get("societytype")
        logo_store_up = request.data.get("logo_store_up")

        if state_store == "true":
            state_store = True
        else:
            state_store = False

        # CREATE MEMBERSHIP REQUEST STORE
        store = Stores.objects.create(
            logo_store_up=logo_store_up,
            name_store=name_store,
            name_legal=name_legal,
            address=address,
            telephone=telephone,
            mobile=mobile,
            email=email,
            number_identifier=number_identifier,
            manager=manager,
            state_store=state_store,
            description=description,
            postal_code=postal_code,
            city=Cities.objects.get(id_city=city),
            storecategories=StoreCategories.objects.get(
                id=storecategories),
            societytype=SocietyType.objects.get(id=societytype))
        store.save()
        id_store = store.id_store
        response = {'id_store': id_store, 'result': 200}
        return Response(response, status=status.HTTP_200_OK)
        # except:
        #     response = {'message': 'Store no create', 'result': 400}
        #     return Response(response, status=status.HTTP_400_BAD_REQUEST)


class LoadDocumentsViewSet(viewsets.ViewSet):
    """
    View to set store.
    """
    authentication_classes = ()
    permission_classes = ()

    def create(self, request):
        try:
            print("Request Data:", request.data)
            print("Request Files:", request.FILES)
            
            url_document = request.FILES.get("url_document")
            documenttype = request.data.get("documenttype")
            store = request.data.get("store")
            
            print("URL Document:", url_document)
            print("Document Type:", documenttype)
            print("Store:", store)

            if not url_document:
                return Response({
                    'message': 'No file was uploaded',
                    'result': 400
                }, status=status.HTTP_400_BAD_REQUEST)

            if not documenttype or not store:
                return Response({
                    'message': 'Missing required fields: documenttype or store',
                    'result': 400
                }, status=status.HTTP_400_BAD_REQUEST)

            # Subir archivo directamente a S3 usando boto3
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )

            # Generar el nombre del archivo con el formato correcto: store_id_document_type.extension
            ext = url_document.name.split('.')[-1].lower()
            file_name = f"{store}_{documenttype}.{ext}"
            
            # Determinar el Content-Type basado en la extensión
            content_type = 'application/octet-stream'  # default
            if ext in ['pdf']:
                content_type = 'application/pdf'
            elif ext in ['jpg', 'jpeg']:
                content_type = 'image/jpeg'
            elif ext in ['png']:
                content_type = 'image/png'
            elif ext in ['doc', 'docx']:
                content_type = 'application/msword'
            elif ext in ['xls', 'xlsx']:
                content_type = 'application/vnd.ms-excel'
            
            # Subir el archivo a S3
            s3_client.upload_fileobj(
                url_document,
                settings.AWS_STORAGE_BUCKET_NAME,
                file_name,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': content_type
                }
            )

            # Crear el registro en la base de datos
            load_document = DocumentsStore.objects.create(
                url_document=file_name,
                documenttype=DocumentType.objects.get(id_document_type=documenttype),
                store=Stores.objects.get(id_store=store))
            load_document.save()
            
            id_documents = load_document.id_documents
            response = {'id_documents': id_documents, 'result': 200}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error:", str(e))
            response = {
                'message': f'Error: {str(e)}',
                'result': 400
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class BankAccountsSaveViewSet(viewsets.ViewSet):
    """
    View to set store.
    """
    authentication_classes = ()
    permission_classes = ()

    def create(self, request):
        try:
            print("Request Data:", request.data)
            print("Request Files:", request.FILES)
            
            account_number = request.data.get("account_number")
            responsible = request.data.get("responsible")
            bank = request.data.get("bank")
            typeaccount = request.data.get("typeaccount")
            store = request.data.get("store")
            state = request.data.get("state")
            certification_url = request.FILES.get("certification_url")
            
            print("Certification URL:", certification_url)
            
            if state == "true":
                state = True
            else:
                state = False

            # Subir archivo directamente a S3 usando boto3
            if certification_url:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )

                # Generar el nombre del archivo con el formato correcto: account_certification_store_id.extension
                ext = certification_url.name.split('.')[-1].lower()
                file_name = f"account_certification_{store}.{ext}"
                
                # Determinar el Content-Type basado en la extensión
                content_type = 'application/octet-stream'  # default
                if ext in ['pdf']:
                    content_type = 'application/pdf'
                elif ext in ['jpg', 'jpeg']:
                    content_type = 'image/jpeg'
                elif ext in ['png']:
                    content_type = 'image/png'
                elif ext in ['doc', 'docx']:
                    content_type = 'application/msword'
                elif ext in ['xls', 'xlsx']:
                    content_type = 'application/vnd.ms-excel'
                
                # Subir el archivo a S3
                s3_client.upload_fileobj(
                    certification_url,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    file_name,
                    ExtraArgs={
                        'ACL': 'public-read',
                        'ContentType': content_type
                    }
                )
            else:
                file_name = None

            # Crear el registro en la base de datos
            load_bank_account = BankAccounts.objects.create(
                account_number=account_number,
                responsible=responsible,
                bank=Banks.objects.get(id_bank=bank),
                typeaccount=TypeAccount.objects.get(id_type_account=typeaccount),
                store=Stores.objects.get(id_store=store),
                state=state,
                certification_url=file_name)
            load_bank_account.save()
            
            id_bank_account = load_bank_account.id_bank_account
            response = {'id_bank_account': id_bank_account, 'result': 200}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error:", str(e))
            response = {
                'message': f'Error: {str(e)}',
                'result': 400
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class StoreDocumentsDataViewSet(viewsets.ViewSet):
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


class BankAccountsViewSet(viewsets.ViewSet):
    serializer_class = BankAccountsSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        id_store = self.request.query_params.get('id_store', None)
        data = ""
        url_bucket_certs = settings.AWS_URL_BUCKET_CERTS
        if id_store is not None:
            account = BankAccounts.objects.get(store_id=id_store)
            data = {
                'id_bank_account': account.id_bank_account,
                'account_number': account.account_number,
                'responsible': account.responsible,
                'bank': account.bank.bank,
                'typeaccount': account.typeaccount.type_account,
                'store': account.store.name_store,
                'store_name_legal': account.store.name_legal,
                'state': account.state,
                'certification_url': url_bucket_certs + str(account.certification_url),
            }
        return Response(data)


class LoadLogoViewSet(viewsets.ViewSet):
    """
    View to set store logo.
    """
    authentication_classes = ()
    permission_classes = ()

    def create(self, request):
        try:
            print("Request Data:", request.data)
            print("Request Files:", request.FILES)
            
            logo_store_up = request.FILES.get("logo_store_up")
            id_store = request.data.get("id_store")
            
            print("Logo File:", logo_store_up)
            print("Store ID:", id_store)

            if not logo_store_up:
                return Response({
                    'message': 'No file was uploaded',
                    'result': 400
                }, status=status.HTTP_400_BAD_REQUEST)

            if not id_store:
                return Response({
                    'message': 'Missing required field: id_store',
                    'result': 400
                }, status=status.HTTP_400_BAD_REQUEST)

            # Subir archivo directamente a S3 usando boto3
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )

            # Generar el nombre del archivo con el formato correcto: store_logo_id.extension
            ext = logo_store_up.name.split('.')[-1].lower()
            file_name = f"logo_{id_store}.{ext}"
            
            # Determinar el Content-Type basado en la extensión
            content_type = 'application/octet-stream'  # default
            if ext in ['jpg', 'jpeg']:
                content_type = 'image/jpeg'
            elif ext in ['png']:
                content_type = 'image/png'
            elif ext in ['gif']:
                content_type = 'image/gif'
            
            # Subir el archivo a S3
            s3_client.upload_fileobj(
                logo_store_up,
                settings.AWS_STORAGE_BUCKET_NAME,
                file_name,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': content_type
                }
            )

            # Actualizar el store con la URL del logo
            store = Stores.objects.get(id_store=id_store)
            store.logo_store_up = file_name
            store.save()

            response = {'message': 'Logo uploaded successfully', 'result': 200}
            return Response(response, status=status.HTTP_200_OK)
            
        except Exception as e:
            print("Error uploading logo:", str(e))
            return Response({
                'message': f'Error uploading logo: {str(e)}',
                'result': 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdatePercentagesStoreViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def update(self, request, pk=None):
        try:
            percentage_payment  = request.data.get("percentage_payment")
            percentage_sale  = request.data.get("percentage_sale")        
            cuc  = request.data.get("cuc")        
            store = Stores.objects.get(id_store=pk)
            store.commission_payment = PaymentPercentages.objects.get(id = percentage_payment) 
            store.commission_sale = PaymentPercentages.objects.get(id = percentage_sale) 
            store.cuc = ConfApiTransaction.objects.get(id = cuc) 
            store.save()
            response = {
                        'message': 'Percentages update correctly',
                        'result': 200
                    }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {
                    'message': 'No Percentages uptate bad request',
                    'result': 400
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

class sendEmailStoreRequestViewSet (viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()
    def create(self, request):
        try:
            subject = 'Solicitud de afiliación recibida'
            template = get_template('mails/request_store_affiliation.html')
            user_mail = request.data['email']
            content = template.render({
                'user_mail': user_mail,
            })
            message = EmailMultiAlternatives(subject, #Titulo
                                            '',
                                            settings.EMAIL_HOST_USER, #Remitente
                                            to=[
                                                user_mail
                                            ]) #Destinatario
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

class sendEmailWelcomeStoreViewSet (viewsets.ModelViewSet):
    authentication_classes = ()
    permission_classes = ()
    def create(self, request):
        try:
            subject = 'Bienvenido a Kompralo!!!'
            template = get_template('mails/approved_store_affiliation.html')
            user_mail = request.data['email']
            content = template.render({
                'user_mail': user_mail,
                'web_url': settings.WEB_URL,
            })
            message = EmailMultiAlternatives(subject, #Titulo
                                            '',
                                            settings.EMAIL_HOST_USER, #Remitente
                                            to=[
                                                user_mail
                                            ]) #Destinatario
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

class GetConfApiTransactionViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    def list(self, request):
        try:
            dataTransactionConf = []            
            conObject = ConfApiTransaction.objects.all()
            for p in conObject:
                dataTransactionConf.append({
                    'id': p.id,
                    'soapcertificate': p.soapcertificate,
                    'soapurl' : p.soapurl,
                    'soappassphrase' : p.soappassphrase,
                    'soapuser' : p.soapuser,
                    'soappassword' : p.soappassword,
                    'cuc' : p.cuc,
                    'terminal' : p.terminal                    
                })
            response = {
                'status': True,
                'data': dataTransactionConf,
                'result': 200
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {
                'message': 'Bad request',
                'result': 400
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


