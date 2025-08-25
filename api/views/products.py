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
from storages.backends.s3boto3 import S3Boto3Storage
import boto3
from django.conf import settings


class CreateProductViewSet(viewsets.ViewSet):
    """
    View to set product.
    """
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def create(self, request):
        # GET DATA FROM FRONTEND
        name_product = request.data.get("name_product")
        description_product = request.data.get("description_product")
        product_code = request.data.get("product_code")
        total_price = request.data.get("total_price")
        availability = request.data.get("availability")
        stock = request.data.get("stock")
        store = request.data.get("store")
        brand = request.data.get("brand")
        discount_price = request.data.get("discount_price")
        subcategory_id = request.data.get("subcategory_id")
        features = request.data.get("subcategory_id")
        published = request.data.get("published")
        state = request.data.get("state")
        image = request.data.get("image")

        # if availability == "true":
        #     availability = True
        # else:
        #     availability = False

        if published == "false":
            published = False
        else:
            published = True

        # CREATE PRODUCT
        n = Products.objects.create(
            name_product=name_product,
            description_product=description_product,
            product_code=product_code,
            total_price=total_price,
            availability=availability,
            stock=stock,
            store_id=store,
            brand=brand,
            discount_price=discount_price,
            features=features,
            # published = published,
            state_id=state,
            subcategory_id=subcategory_id,
            image=image)
        n.save()
        data = n.id_product
        response = {'id_product': data, 'result': 200}
        return Response(response, status=status.HTTP_200_OK)


class ProductDeleteViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    @action(detail=True, methods=['POST'])
    def delete_image(self, request, pk=None):
        if 'image' in request.data:
            image = request.data['image']
            try:
                product = Products.objects.get(id_product=pk)
                product.image = image
                product.save()
                serializer = ProductsSerializer(product, many=False)
                response = {
                    'message': 'Rating update',
                    'result': serializer.data
                }
                return Response(response, status=status.HTTP_200_OK)
            except:
                response = {'message': 'you need to provide image name ....'}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {'message': 'you need to provide image name'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ProductDeleteImageViewSet(viewsets.ModelViewSet):
    queryset = Images.objects.all()
    serializer_class = ImagesSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    @action(detail=True, methods=['POST', 'DELETE', 'PUT'])
    def action_image(self, request, pk=None):
        # http://127.0.0.1:8000/api/delete_product_image/41/action_image/
        if request.method == 'DELETE':
            try:
                image_product = Images.objects.get(id=pk)
                image_product.delete()
                response = {
                    'message': 'Image delete correctly',
                    'result': 200,
                    'image': image_product.image
                }
                return Response(response, status=status.HTTP_200_OK)
            except:
                response = {'message': 'No find image', 'result': 400}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ProductsFrontStoreViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    authentication_classes = ()
    permission_classes = ()

    def get_queryset(self):
        """http://127.0.0.1:8000/api/store_products_front?id_store=1"""
        queryset = Products.objects.all()
        id_store = self.request.query_params.get('id_store', None)
        if id_store is not None:
            queryset = Products.objects.filter(store_id=id_store,
                                                published=True,
                                                state_id=2)
        return queryset


class ProductsViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """http://127.0.0.1:8000/api/products?id_store=1"""
        queryset = Products.objects.all()
        id_store = self.request.query_params.get('id_store', None)
        if id_store is not None:
            queryset = Products.objects.filter(store_id=id_store)
        return queryset

    @action(detail=True, methods=['POST', 'DELETE', 'PUT'])
    def action_product(self, request, pk=None):
        if request.method == 'POST':
            if 'image' in request.data:
                image = request.data['image']
                try:
                    product = Products.objects.get(id_product=pk)
                    product.image = image
                    product.save()
                    serializer = ProductsSerializer(product, many=False)
                    response = {
                        'message': 'Rating update',
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
            try:
                images_product = Images.objects.filter(product_id=pk)
                for p in images_product:
                    image = Images.objects.get(id = p.id)
                    image.image.delete(save=False)
                    image.delete()
                product = Products.objects.get(id_product=pk)
                product.delete()
                response = {
                    'message': 'Product delete correctly',
                    'result': 200
                }
                return Response(response, status=status.HTTP_200_OK)
            except:
                response = {'message': 'No find product', 'result': 400}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'PUT':
            # try:
            if request.data['edit_pr'] is not None:
                # EDIT PRODUCT GENERAL
                name_product = request.data['name_product']
                description_product = request.data['description_product']
                product_code = request.data['product_code']
                total_price = request.data['total_price']
                availability = request.data['availability']

                stock = request.data['stock']
                brand = request.data['brand']
                subcategory = request.data['subcategory']
                # discount_price = request.data['discount_price']

                if availability == True:
                    availability = True
                else:
                    availability = False

                product = Products.objects.get(id_product=pk)
                product.name_product = name_product
                product.description_product = description_product
                product.product_code = product_code
                product.total_price = total_price
                product.availability = availability
                product.stock = stock
                product.brand = brand
                product.subcategory_id = subcategory
                # product.discount_price = discount_price
                product.save()
            else:
                # EDIT STATUS PRODUCT
                state = request.data['state']
                product = Products.objects.get(id_product=pk)
                product.state_id = state
                product.save()
            response = {
                'message': 'Product update state correctly',
                'result': 200
            }
            return Response(response, status=status.HTTP_200_OK)
            # except:
            #     response = {'message': 'No put state', 'result': 400}
            #     return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PUT'])
    def action_product_state(self, request, pk=None):
        if request.method == 'PUT':
            if request.data['state'] is not None:
                product = Products.objects.get(id_product=pk)
                product.state_id = request.data['state']
                product.save()
                response = {
                    'message': 'Product delete correctly',
                    'result': 200
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    'message': 'You have send state field', 'result': 400}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

class UpdateStockViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def update(self, request, pk=None):
        print(pk)
        try:
            newstock  = request.data.get("newstock")
            product = Products.objects.get(id_product=pk)
            product.stock = newstock
            product.save()
            print(newstock)
            if product.stock == 0 :
                product.availability = False
                product.save()
            else:
                product.availability = True
                product.save()
            response = {
                        'message': 'Stock update correctly',
                        'result': 200
                    }
            return Response(response, status=status.HTTP_200_OK)
        except:
            response = {
                    'message': 'No discount stock or bad request',
                    'result': 400
                }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

class ProductsNavStoreViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsFrontStoreSerializer
    authentication_classes = ()
    permission_classes = ()

    def get_queryset(self):
        """http://127.0.0.1:8000/api/products?id_store=1"""
        # queryset = Products.objects.filter(state_id="2", availability = True).order_by('-id_product')[:30]
        queryset = Products.objects.filter(state_id="2", availability = True).order_by('?')[:30]
        return queryset

class ProductsNavStoreView(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsFrontStoreSerializer
    authentication_classes = ()
    permission_classes = ()

    def get_queryset(self):
        """http://127.0.0.1:8000/api/products?id_store=1"""
        queryset = Products.objects.filter(state_id="2")
        return queryset
    
class ProductsConfirmViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsFrontStoreSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )


class ProductSubcategoryNavStoreViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsFrontStoreSerializer
    authentication_classes = ()
    permission_classes = ()

    def get_queryset(self):
        """http://127.0.0.1:8000/api/product_subcategory?subcategory_id=1"""
        subcategory_id = self.request.query_params.get('subcategory_id', None)
        id_store = self.request.query_params.get('id_store', None)

        if id_store is not None:
            print("entra 1")
            queryset = Products.objects.filter(subcategory_id=subcategory_id,
                                               state_id=2,
                                               store_id=id_store,
                                               published=True)
        else:
            print("entra 2")
            queryset = Products.objects.filter(subcategory_id=subcategory_id,
                                               state_id=2,
                                               published=True)
        return queryset


class ProducsCategoriesViewSet(viewsets.ViewSet):
    serializer_class = ProductsSerializer
    authentication_classes = ()
    permission_classes = ()

    def list(self, request):
        id_category = self.request.query_params.get('id_category', None)
        id_store = self.request.query_params.get('id_store', None)

        if id_store is not None:
            sql = 'select * from api_products pr left ' \
                  'join api_subcategories sub on sub.id = pr.subcategory_id ' \
                  'where state_id = 2 and sub.category_id =' + id_category + \
                'and pr.store_id = ' + id_store + 'and pr.published = True'
        else:
            sql = 'select * from api_products pr left ' \
                  'join api_subcategories sub on sub.id = pr.subcategory_id where state_id = 2 and sub.category_id =' + \
                id_category + 'and pr.published = True'
                

        data = []

        for p in Products.objects.raw(sql):
            data.append({
                'name_product': p.name_product,
                'image': p.image,
                'total_price': p.total_price,
                'product_code': p.product_code,
                'brand': p.brand,
                'availability': p.availability,
                'discount_price': p.discount_price,
                'id_product': p.id_product,
                'store': p.store_id,
                'category': p.category_id,
                'id_product': p.id_product,
                'created_at':p.created_at,
                'description_product': p.description_product,
                'stock':p.stock,
                'subcategory':p.subcategory_id,
                'category_type':p.category_type,
                'features':p.features,
                'rating':p.rating,
                'state':p.state_id,
                'color':"null",
                "size":"null",
                "image":p.image
                
            })
        return Response(data)


class AdminProductsViewSet(viewsets.ViewSet):
    serializer_class = AdminProductSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        data = []
        for p in Products.objects.raw(
                'select pr.*, st.name_store, cate.name_category as namecategory ,cat.name_subcategory as namesubcategory, sta.name_state from api_products pr join api_stores st on st.id_store = pr.store_id join api_subcategories cat on cat.id = pr.subcategory_id join api_categories cate on cate.id = cat.category_id join api_productstate sta on sta.id = pr.state_id order by id_product desc;'
        ):
            data.append({
                'id_product': p.id_product,
                'created_at': p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'name_product': p.name_product,
                'name_store': p.name_store,
                'namecategory': p.namecategory,
                'namesubcategory': p.namesubcategory,
                'product_code': p.product_code,
                'total_price': p.total_price,
                'published': p.published,
                'name_state': p.name_state
            })
        return Response(data)


"""Views to front store"""


class SearchProductViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    authentication_classes = ()
    permission_classes = ()

    def get_queryset(self):
        """http://127.0.0.1:8000/api/product_filter?string_search=sup"""
        queryset = Products.objects.all()
        string_search = self.request.query_params.get('string_search', None)
        print(string_search)
        if string_search is not None:
            queryset = Products.objects.filter(
                name_product__icontains=string_search, state_id=2)
        return queryset


class GetLatestImageViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        data = ""
        sql = 'select * from api_images order by id desc limit 1'
        for p in Images.objects.raw(sql):
            data = {
                'id': p.id
            }
        return Response(data)


class GetCountImageProductViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def list(self, request):        
        id_prod = self.request.query_params.get('id_product', None);
        data = ""        
        count_img_prod = Images.objects.filter(product_id=id_prod).count()        
        data = count_img_prod
        return Response(data)


class LoadImageProductsViewSet(viewsets.ViewSet):
    authentication_classes = ()
    permission_classes = ()

    def create(self, request):
        try:
            print("Request Data:", request.data)
            print("Request Files:", request.FILES)
            
            image = request.FILES.get("image")
            product = request.data.get("product")
            image_name = request.data.get("image_name")
            
            print("Image File:", image)
            print("Product ID:", product)
            print("Image Name:", image_name)

            if not image:
                return Response({
                    'message': 'No file was uploaded',
                    'result': 400
                }, status=status.HTTP_400_BAD_REQUEST)

            if not product:
                return Response({
                    'message': 'Missing required field: product',
                    'result': 400
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validar que el producto existe
            try:
                product_obj = Products.objects.get(id_product=product)
            except Products.DoesNotExist:
                return Response({
                    'message': 'Product does not exist',
                    'result': 400
                }, status=status.HTTP_400_BAD_REQUEST)

            # Subir archivo directamente a S3 usando boto3
            try:
                # Usar la misma configuración que funciona en otras partes
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )

                # Generar el nombre del archivo
                ext = image.name.split('.')[-1].lower()
                print("Image Name:", image_name)
                file_name = image_name
                
                # Determinar el Content-Type basado en la extensión
                content_type = 'application/octet-stream'  # default
                if ext in ['jpg', 'jpeg']:
                    content_type = 'image/jpeg'
                elif ext in ['png']:
                    content_type = 'image/png'
                elif ext in ['gif']:
                    content_type = 'image/gif'
                
                print("Uploading to S3:", {
                    'bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'file_name': file_name,
                    'content_type': content_type
                })

                # Subir el archivo a S3
                s3_client.upload_fileobj(
                    image,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    file_name,
                    ExtraArgs={
                        'ACL': 'public-read',
                        'ContentType': content_type
                    }
                )

                # Crear el registro en la base de datos
                load_image = Images.objects.create(
                    image=file_name,
                    image_name=image_name,
                    product=product_obj)
                load_image.save()
                
                id_image = load_image.id
                response = {'id_image': id_image, 'result': 200}
                return Response(response, status=status.HTTP_200_OK)

            except Exception as s3_error:
                print("S3 Error:", str(s3_error))
                return Response({
                    'message': f'S3 Error: {str(s3_error)}',
                    'result': 500
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            print("Error uploading image:", str(e))
            return Response({
                'message': f'Error uploading image: {str(e)}',
                'result': 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteImageProductsViewSet(viewsets.ViewSet):
    authentication_classes = ()
    permission_classes = ()

    def create(self, request):
        try:
            print("Request Data:", request.data)
            image_id = request.data.get("image_id")
            
            if not image_id:
                return Response({
                    'message': 'Missing required field: image_id',
                    'result': 400
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Obtener la imagen y verificar que existe
                image = Images.objects.get(id=image_id)
                product_id = image.product_id

                # Eliminar la imagen de S3
                try:
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        region_name=settings.AWS_S3_REGION_NAME
                    )
                    s3_client.delete_object(    
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=image.image
                    )   
                except Exception as s3_error:
                    print("Error deleting from S3:", str(s3_error))
                    # Continuamos con la eliminación de la base de datos incluso si falla S3

                # Eliminar el registro de la base de datos
                image.delete()

                # Actualizar la imagen principal del producto si es necesario
                try:
                    all_prod_img = Images.objects.filter(product_id=product_id).order_by('-id')
                    if all_prod_img.exists():
                        get_image_name = all_prod_img.first().image_name
                        prod = Products.objects.get(id_product=product_id)
                        prod.image = get_image_name
                        prod.save()
                except Exception as update_error:
                    print("Error updating product image:", str(update_error))

                response = {
                    'message': 'Image deleted successfully',
                    'id_image': image_id,
                    'result': 200
                }
                return Response(response, status=status.HTTP_200_OK)

            except Images.DoesNotExist:
                return Response({
                    'message': 'Image not found',
                    'result': 404
                }, status=status.HTTP_404_NOT_FOUND)
            except Products.DoesNotExist:
                return Response({
                    'message': 'Product not found',
                    'result': 404
                }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print("Error deleting image:", str(e))
            return Response({
                'message': f'Error deleting image: {str(e)}',
                'result': 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class VerifyStockProductsViewSet(viewsets.ViewSet):
    serializer_class = AdminProductSerializer
    authentication_classes = ()
    permission_classes = ()

    def list(self, request):
        data_response = False;

        # odelsExample.objects.filter(id=showid).values('title')
        stock_product = Products.objects.filter(id_product=35).values('stock')
        stock_product = stock_product[0]['stock']
        print (stock_product)

        if stock_product > 0:
            data_response = True
       
        return Response(data_response)




