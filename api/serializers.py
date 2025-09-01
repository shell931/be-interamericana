from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response


class GetGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'first_name', 'last_name', 'email',
            'is_active', 'group_id', 'store', 'type_user', 'type_identifier',
            'number_identifier'
        ]
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        group_id = self.data['group_id']
        my_group = Group.objects.get(id=group_id)
        my_group.user_set.add(user.id)
        return user


class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()


class TypeIdentificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeIdentification
        fields = ['id', 'type_identifier']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = [
            'id_menu', 'name_menu', 'icon_menu', 'route_menu', 'state_menu'
        ]


class DepartmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = ['id_departament', 'departament']


class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cities
        fields = ['id_city', 'city', 'id_departament']


class StoreCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreCategories
        fields = ['id', 'created_at', 'name_category', 'icon']


class SocietyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocietyType
        fields = ['id', 'created_at', 'society_type']


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banks
        fields = ['id_bank', 'created_at', 'bank']


class TypeAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeAccount
        fields = ['id_type_account', 'created_at', 'type_account']


class StoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stores
        fields = [
            'id_store', 'created_at', 'name_store', 'address', 'telephone',
            'email', 'number_identifier', 'manager', 'state_store', 'city',
            'logo_store', 'description', 'storecategories', 'logo_store_up'
        ]

class BankAccountsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'id_bank_account', 'created_at', 'account_number', 'responsible', 'bank', 'typeaccount', 'store', 'State', 'certification_url'
        ]


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ("image", )


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ("id", "image", "product")


class ColorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colors
        fields = ("id_color", "color")


class SizesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sizes
        fields = ("id_size", "size")


class ProductsSerializer(serializers.ModelSerializer):
    rel_product = ImagesSerializer(many=True)
    color = ColorsSerializer(many=True)
    size = SizesSerializer(many=True)

    class Meta:
        model = Products
        fields = [
            'id_product', 'created_at', 'name_product', 'description_product',
            'product_code', 'total_price', 'availability', 'stock', 'store',
            'brand', 'subcategory', 'category_type', 'discount_price',
            'features', 'rating', 'state', 'color', 'size', 'image',
            'published', 'rel_product'
        ]


class AdminProductsSerializer(serializers.Serializer):
    class Meta:

        fields = ['id_product', 'name_product', 'name_store', 'name_category']


class ProductsFrontStoreSerializer(serializers.ModelSerializer):
    rel_product = ImagesSerializer(many=True)
    color = ColorsSerializer(many=True)
    size = SizesSerializer(many=True)

    class Meta:
        model = Products
        fields = [
            'id_product', 'created_at', 'name_product', 'description_product',
            'product_code', 'total_price', 'availability', 'stock', 'store',
            'brand', 'subcategory', 'category_type', 'discount_price',
            'features', 'rating', 'state', 'color', 'size', 'image',
            'rel_product'
        ]


class SubCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategories
        fields = ("id", "name_subcategory", "category")


class CategoriesSerializer(serializers.ModelSerializer):
    rel_categories = SubCategoriesSerializer(many=True)

    class Meta:
        model = Categories
        fields = ("id", "name_category", "rel_categories", "icon", "active")


class AdminProductSerializer(serializers.Serializer):
    id_product = serializers.IntegerField(read_only=True)
    created_at = serializers.DateField('creation date')
    name_product = serializers.CharField(max_length=256)
    name_store = serializers.CharField(max_length=256)
    name_subcategory = serializers.CharField(max_length=100)
    product_code = serializers.CharField(max_length=30)
    total_price = serializers.DecimalField(max_digits=13, decimal_places=2)
    published = serializers.BooleanField('Published', default=True)


class LocationClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationClient
        fields = ("id", "created_at", "city", "neighborhood", "via", "number",
                  "sn", "additional_data", "phone", "contact", "latitude",
                  "longitude", "user", "predetermined")


class LocationClientByUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    neighborhood = serializers.CharField(max_length=100)
    number = serializers.CharField(max_length=100)
    via = serializers.CharField(max_length=100)
    sn = serializers.CharField(max_length=100)
    additional_data = serializers.CharField(max_length=500)
    phone = serializers.CharField(max_length=500)
    contact = serializers.CharField(max_length=100)
    nameci = serializers.CharField(max_length=100)
    departament = serializers.CharField(max_length=100)
    predetermined = serializers.BooleanField('Published', default=True)


class InvoiceDetalSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceDetail
        fields = ("id", "created_at", "name_product", "description_product",
                  "product_code", "unit_price", "quantity", "total_price",
                  "id_invoice", "id_product", "name_pr")


class InvoiceSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    reference = serializers.CharField(max_length=100)
    id_store_id = serializers.CharField(max_length=100)
    created_at = serializers.CharField(max_length=100)
    reference_invoice = serializers.CharField(max_length=100)
    total_price = serializers.CharField(max_length=100)
    percentage_sale = serializers.CharField(max_length=100)
    val_percentage_sale = serializers.CharField(max_length=100)
    percentage_commision_payment = serializers.CharField(max_length=100)
    val_percentage_commision_payment = serializers.CharField(max_length=100)
    percentage_rete_ica = serializers.CharField(max_length=100)
    val_percentage_rete_ica = serializers.CharField(max_length=100)
    percentage_rete_fuente = serializers.CharField(max_length=100)
    val_percentage_rete_fuente = serializers.CharField(max_length=100)
    percentage_commision_tax = serializers.CharField(max_length=100)
    val_percentage_commision_tax = serializers.CharField(max_length=100)
    total_balance = serializers.CharField(max_length=100)
    name_client = serializers.CharField(max_length=100)
    first_name_client = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=100)
    adress = serializers.CharField(max_length=100)
    number_identifier = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=100)
    id_store_id = serializers.CharField(max_length=100)
    state_id = serializers.CharField(max_length=100)
    user_id = serializers.CharField(max_length=100)
    transaction_id = serializers.CharField(max_length=100)
    nameci = serializers.CharField(max_length=100)
    departament = serializers.CharField(max_length=100)
    name_store = serializers.CharField(max_length=100)
    paymentmethod = serializers.CharField(max_length=100)
    name_state = serializers.CharField(max_length=100)
    type_identifier = serializers.CharField(max_length=100)
    quot = serializers.CharField(max_length=100)
    brand = serializers.CharField(max_length=100)
    num_aprob = serializers.CharField(max_length=100)
    cod_reply = serializers.CharField(max_length=100)
    messaje_reply = serializers.CharField(max_length=100)
    num_recibo = serializers.CharField(max_length=100)
    canceled = serializers.CharField(max_length=100)
    type_service = serializers.CharField(max_length=100)
    type_service_id = serializers.CharField(max_length=100)
    getBinnacleFalse = serializers.CharField(max_length=100)


class BankAccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccounts
        fields = [
            'id_bank_account', 'created_at', 'account_number', 'responsible', 'bank', 'typeaccount', 'store ', 'state', 'certification_url'
        ]


class PaymentPercentagesSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPercentages
        fields = ['id', 'percentage', 'description', 'state_percentage', 'type_percentage']

class TransactionDataSerializer(serializers.ModelSerializer):
    class Meta:

        fields = ['id']

class GetBinnaclesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Binnacle
        fields = ['id','created_at','observation','id_invoice_id','user_id']