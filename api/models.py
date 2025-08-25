from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import Group
from storages.backends.s3boto3 import S3Boto3Storage
from django.template import loader

from django.template.loader import get_template
import time
from django.conf import settings
"""ADMIN MODELS"""


class Menu(models.Model):
    id_menu = models.AutoField(primary_key=True)
    name_menu = models.CharField(max_length=200, blank=False, null=False)
    icon_menu = models.CharField(max_length=200, blank=False, null=False)
    route_menu = models.CharField(max_length=200, blank=False, null=False)
    state_menu = models.BooleanField('Estate', default=True)

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'

    def __str__(self):
        return self.name_menu


class TypeUser(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    type = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name = 'Type_user'
        verbose_name_plural = 'Type_users'

    def __str__(self):
        return self.type


class TypeIdentification(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=True,
                                  auto_now_add=False)
    type_identifier = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name = 'Type_identifier'
        verbose_name_plural = 'Type_identifiers'

    def __str__(self):
        return self.type


Group.add_to_class('menu', models.ManyToManyField(Menu))
User.add_to_class('group_id', models.IntegerField(null=True))
User.add_to_class(
    'type_user',
    models.ForeignKey(TypeUser, on_delete=models.CASCADE, null=True))
User.add_to_class(
    'type_identifier',
    models.ForeignKey(TypeIdentification, on_delete=models.CASCADE, null=True))
User.add_to_class('number_identifier',
                  models.CharField(max_length=100, null=True))
"""BUSINESS MODELS"""


class Countries(models.Model):
    id_country = models.AutoField(primary_key=True)
    country = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.departament


class Departments(models.Model):
    id_departament = models.AutoField(primary_key=True)
    departament = models.CharField(max_length=100, blank=False, null=False)
    country = models.ForeignKey(
        Countries, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.departament


class Cities(models.Model):
    id_city = models.AutoField(primary_key=True)
    city = models.CharField(max_length=100, blank=False, null=False)
    id_departament = models.ForeignKey(Departments, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'

    def __str__(self):
        return self.city


class StoreCategories(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                      auto_now=False,
                                      auto_now_add=True)
    name_category = models.CharField(max_length=200, blank=False, null=False)
    icon = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name_category


class SocietyType(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                      auto_now=False,
                                      auto_now_add=True)
    society_type = models.CharField(
        max_length=200, blank=True, null=True, default='Régimen Simplificado')

    class Meta:
        verbose_name = 'Society Type'
        verbose_name_plural = 'Society Type'

    def __str__(self):
        return self.society_type


class TypePercentage(models.Model):
    id = models.AutoField(primary_key=True)
    type_percentage = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name = 'Type_Prcentage'
        verbose_name_plural = 'Types_Prcentages'

    def __str__(self):
        return self.type_percentage


class PaymentPercentages(models.Model):
    id = models.AutoField(primary_key=True)
    percentage = models.DecimalField(
        max_digits=13, decimal_places=3, null=True)
    description = models.CharField(max_length=200, null=True)
    state_percentage = models.BooleanField('Estate Percentage', default=True)
    type_percentage = models.ForeignKey(TypePercentage,
                                        on_delete=models.CASCADE,
                                        related_name='rel_type_percentage')

    class Meta:
        verbose_name = 'Payment_Prcentage'
        verbose_name_plural = 'Payments_Prcentages'

    def __str__(self):
        return str(self.percentage) if self.percentage is not None else ''


class ConfApiTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                      auto_now=False,
                                      auto_now_add=True)
    soapcertificate = models.CharField(max_length=300, null=True)
    soapurl = models.CharField(max_length=300, null=True)
    soappassphrase = models.CharField(max_length=300, null=True)
    soapuser = models.CharField(max_length=300, null=True)
    soappassword = models.CharField(max_length=300, null=True)
    cuc = models.CharField(max_length=300, null=True)
    terminal = models.CharField(max_length=300, null=True)

    class Meta:
        verbose_name = 'ConfApiTransaction'
        verbose_name_plural = 'ConfApiTransactions'

    def __str__(self):
        return self.cuc


class Stores(models.Model):
    id_store = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(
        'creation date', auto_now=False, auto_now_add=True)
    name_store = models.CharField(max_length=100, blank=False, null=False)
    name_legal = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200, blank=False, null=False)
    telephone = models.CharField(max_length=100, blank=False, null=False)
    mobile = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=False, null=False)
    number_identifier = models.CharField(
        max_length=100, blank=False, null=False)
    manager = models.CharField(max_length=200, blank=False, null=False)
    state_store = models.BooleanField('State', default=True)
    city = models.ForeignKey(Cities, on_delete=models.CASCADE, null=True)
    logo_store = models.CharField(max_length=200, blank=False, null=False)
    logo_store_up = models.FileField(
        storage=S3Boto3Storage(bucket_name='market-docus-v2'), null=True)
    description = models.TextField(max_length=500, null=True)
    storecategories = models.ForeignKey(
        StoreCategories, on_delete=models.CASCADE, related_name='rel_storecategories')
    postal_code = models.CharField(max_length=100, blank=True, null=True)
    societytype = models.ForeignKey(
        SocietyType, on_delete=models.CASCADE, related_name='rel_societytype', null=True)
    commission_payment = models.ForeignKey(
        PaymentPercentages, on_delete=models.CASCADE, related_name='rel_paymentpercentage', null=True)
    commission_sale = models.ForeignKey(
        PaymentPercentages, on_delete=models.CASCADE, related_name='rel_salepercentage', null=True)
    cuc = models.ForeignKey(
        ConfApiTransaction, on_delete=models.CASCADE, related_name='rel_cuc', null=True)

    def save(self, *args, **kwargs):
        ext = self.logo_store_up.name
        ext = ext.split('.')[-1]
        self.logo_store_up.name = 'logo_'+str(self.id_store)+'.'+ext
        super(Stores, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'

    def __str__(self):
        return self.name_store


class DocumentType(models.Model):
    id_document_type = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(
        'creation date', auto_now=False, auto_now_add=True)
    type = models.CharField(max_length=200, blank=False, null=False)

    class Meta:
        verbose_name = 'Document type'
        verbose_name_plural = 'Document type'

    def __str__(self):
        return self.type


class DocumentsStore(models.Model):
    id_documents = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(
        'creation date', auto_now=False, auto_now_add=True)
    url_document = models.FileField(
        storage=S3Boto3Storage(bucket_name='market-docus-v2'))
    documenttype = models.ForeignKey(
        DocumentType, on_delete=models.CASCADE, related_name='rel_documenttype')
    store = models.ForeignKey(
        Stores, on_delete=models.CASCADE, related_name='rel_stores', null=True)

    def save(self, *args, **kwargs):
        ext = self.url_document.name
        ext = ext.split('.')[-1]
        document_type = self.documenttype.id_document_type
        self.url_document.name = str(
            self.store.id_store)+'_'+str(document_type)+'.'+ext
        super(DocumentsStore, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'url_document'
        verbose_name_plural = 'url_document'

    def __str__(self):
        return self.url_document


class Banks(models.Model):
    id_bank = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(
        'creation date', auto_now=False, auto_now_add=True)
    bank = models.CharField(max_length=200, blank=False, null=False)

    class Meta:
        verbose_name = 'bank'
        verbose_name_plural = 'bank'

    def __str__(self):
        return self.bank


class TypeAccount(models.Model):
    id_type_account = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(
        'creation date', auto_now=False, auto_now_add=True)
    type_account = models.CharField(max_length=200, blank=False, null=False)

    class Meta:
        verbose_name = 'type_account'
        verbose_name_plural = 'type_account'

    def __str__(self):
        return self.type_account


class BankAccounts(models.Model):
    id_bank_account = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(
        'creation date', auto_now=False, auto_now_add=True)
    account_number = models.CharField(max_length=200, blank=False, null=False)
    responsible = models.CharField(max_length=200, blank=False, null=False)
    bank = models.ForeignKey(
        Banks, on_delete=models.CASCADE, related_name='rel_bank', null=True)
    typeaccount = models.ForeignKey(
        TypeAccount, on_delete=models.CASCADE, related_name='rel_typeaccount', null=True)
    store = models.ForeignKey(
        Stores, on_delete=models.CASCADE, related_name='rel_stores_acc', null=True)
    state = models.BooleanField('State', default=True)
    certification_url = models.FileField(
        storage=S3Boto3Storage(bucket_name='market-docus-v2'))

    def save(self, *args, **kwargs):
        ext = self.certification_url.name
        ext = ext.split('.')[-1]
        self.certification_url.name = 'account_certification_' + \
            str(self.store.id_store)+'.'+ext
        super(BankAccounts, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'account_number'
        verbose_name_plural = 'account_number'

    def __str__(self):
        return self.account_number


User.add_to_class(
    'store', models.ForeignKey(Stores, on_delete=models.CASCADE, null=True))


class Colors(models.Model):
    id_color = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    color = models.CharField(max_length=20, blank=False, null=False)

    class Meta:
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'

    def __str__(self):
        return self.color


class Sizes(models.Model):
    id_size = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    size = models.CharField(max_length=20, blank=False, null=False)

    class Meta:
        verbose_name = 'Size'
        verbose_name_plural = 'Sizes'

    def __str__(self):
        return self.size


class Categories(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    name_category = models.CharField(max_length=100, blank=False, null=False)
    icon = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name_category


class SubCategories(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    name_subcategory = models.CharField(max_length=100,
                                        blank=False,
                                        null=False)
    category = models.ForeignKey(Categories,
                                 on_delete=models.CASCADE,
                                 related_name='rel_categories')

    class Meta:
        verbose_name = 'Subcategory'
        verbose_name_plural = 'Subcategories'

    def __str__(self):
        return self.name_subcategory


class ProductState(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    name_state = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=500, null=True)

    class Meta:
        verbose_name = 'Product_state'
        verbose_name_plural = 'Product_states'

    def __str__(self):
        return self.name_state


class Products(models.Model):
    id_product = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    name_product = models.CharField(max_length=100, blank=False, null=False)
    description_product = models.TextField(max_length=1000,
                                           blank=False,
                                           null=False)
    product_code = models.CharField(max_length=30, blank=False, null=False)
    total_price = models.DecimalField(max_digits=13, decimal_places=2)
    availability = models.BooleanField('Estate', default=True)
    stock = models.IntegerField(null=True)
    store = models.ForeignKey(Stores,
                              on_delete=models.CASCADE,
                              null=True,
                              related_name='rel_store')
    brand = models.CharField(max_length=100, null=True)
    subcategory = models.ForeignKey(SubCategories,
                                    on_delete=models.CASCADE,
                                    related_name='rel_category')
    category_type = models.CharField(max_length=100, null=True)
    discount_price = models.DecimalField(max_digits=13,
                                         decimal_places=2,
                                         null=True)
    features = models.CharField(max_length=200, null=True)
    rating = models.IntegerField(null=True)
    color = models.ManyToManyField(Colors)
    image = models.CharField(max_length=300, null=True)
    size = models.ManyToManyField(Sizes)
    published = models.BooleanField('Published', default=True)
    state = models.ForeignKey(ProductState,
                              on_delete=models.CASCADE,
                              related_name='rel_state')

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name_product


class Images(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    product = models.ForeignKey(Products,
                                on_delete=models.CASCADE,
                                related_name='rel_product',
                                blank=True,
                                null=True)
    image = models.FileField(
        storage=S3Boto3Storage(bucket_name='market-docus-v2'))
    image_name = models.CharField(max_length=200, null=True, blank=True)

    def save(self, *args, **kwargs):
        ext = self.image.name
        ext = ext.split('.')[-1]
        print(self.image_name)
        self.image.name = str(self.image_name)
        super(Images, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'images'

    def __str__(self):
        return self.image


class LocationClient(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    city = models.ForeignKey(Cities, on_delete=models.CASCADE, null=False)
    neighborhood = models.CharField(max_length=300, null=False)
    number = models.CharField(max_length=200, null=False)
    via = models.CharField(max_length=200, null=False)
    sn = models.CharField(max_length=200, null=False)
    additional_data = models.TextField(max_length=500, null=True)
    phone = models.CharField(max_length=200, null=False)
    contact = models.CharField(max_length=200, null=False)
    latitude = models.CharField(max_length=200, null=False)
    longitude = models.CharField(max_length=200, null=False)
    predetermined = models.BooleanField('predetermined', default=False)
    user = models.ManyToManyField(User)


class PaymentMethod(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    paymentmethod = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name = 'Type_user'
        verbose_name_plural = 'Type_users'

    def __str__(self):
        return self.type

class TypeServices(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    service = models.CharField(max_length=200, null=True)                                

    class Meta:
        verbose_name = 'Type_Service'
        verbose_name_plural = 'Type_Services'

    def __str__(self):
        return self.type


class InvoiceState(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    name_state = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=500, null=True)

    class Meta:
        verbose_name = 'Invoice_state'
        verbose_name_plural = 'Invoice_states'

    def __str__(self):
        return self.name_state


class InvoiceExternalState(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    name_state = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=500, null=True)

    class Meta:
        verbose_name = 'Invoice_external_state'
        verbose_name_plural = 'Invoice_external_states'

    def __str__(self):
        return self.name_state


class CheckValidationSale(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                      auto_now=False,
                                      auto_now_add=True)
    name_check = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=500, null=True)

    class Meta:
        verbose_name = 'Name_check'
        verbose_name_plural = 'Name_checks'

    def __str__(self):
        return self.name_check



class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    reference = models.CharField(max_length=200, null=False)
    reference_invoice = models.CharField(max_length=200, null=False)
    reference_checkout = models.CharField(max_length=200, null=True, blank=True)
    id_store = models.ForeignKey(Stores,
                                 on_delete=models.CASCADE,
                                 related_name='rel_store_invoice')
    total_price = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    percentage_sale = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    val_percentage_sale = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    percentage_commision_payment = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    val_percentage_commision_payment = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    percentage_rete_ica = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    val_percentage_rete_ica = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    percentage_rete_fuente = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    val_percentage_rete_fuente = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    val_percentage_rete_iva = models.DecimalField(
        max_digits=13, decimal_places=2, null=True) 
    percentage_commision_tax = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    val_percentage_commision_tax = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    total_balance = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    val_taxable_base = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    val_tax = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    state = models.ForeignKey(InvoiceState,
                              on_delete=models.CASCADE,
                              related_name='rel_state_invoice')
    external_state = models.ForeignKey(InvoiceExternalState,
                            on_delete=models.CASCADE,
                            related_name='rel_external_state_invoice', null=True)
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        related_name='rel_paymentmethod_invoice')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='rel_user_invoice')
    name_client = models.CharField(max_length=200, null=False)
    first_name_client = models.CharField(max_length=200, null=False)
    phone = models.CharField(max_length=100, null=False)
    city = models.ForeignKey(Cities,
                             on_delete=models.CASCADE,
                             related_name='rel_city_invoice', null=True)
    adress = models.TextField(max_length=500, null=True)
    type_identification = models.ForeignKey(
        TypeIdentification,
        on_delete=models.CASCADE,
        related_name='rel_typeidenti_invoice')
    number_identifier = models.CharField(max_length=100, null=False)
    email = models.CharField(max_length=200, null=False)
    transaction_id = models.BigIntegerField(null=True)
    shipping_voucher = models.FileField(
        storage=S3Boto3Storage(bucket_name='market-docus-v2'), null=True)
    letter_received = models.FileField(
        storage=S3Boto3Storage(bucket_name='market-docus-v2'), null=True,default=None)
    transfer_id = models.BigIntegerField(null=True)
    canceled = models.BooleanField('canceled', default=False)
    contra = models.BooleanField('contra', default=False)
    type_service = models.ForeignKey(TypeServices,
                        on_delete=models.CASCADE,
                        related_name='rel_external_type_service', null=True)
    paid_trade = models.BooleanField('paid_trade', default=False)                    
    canceled_in_transfer = models.BooleanField('canceled_in_transfer', default=False)
    check_call_control = models.BooleanField('check_call_control', default=False)
    check_record = models.BooleanField('check_record', default=False)
    check_shipment = models.BooleanField('check_shipment', default=False)
    check_finaly = models.BooleanField('check_finaly', default=False)


    def save(self, *args, **kwargs):
        ext = self.shipping_voucher.name
        ext = ext.split('.')[-1]
        self.shipping_voucher.name = 's_v' + '_' + str(
            self.id)+'_'+str(
            self.reference_invoice)+'.'+ext
        ext_l = self.letter_received.name
        if ext_l is None:
            self.letter_received.name = ""
            ext_l = ""
            self.letter_received.name = 'l_r' + '_' + str(
                self.id)+'_'+str(
                self.reference_invoice)+'.'+ext_l
        else:
            ext_l = ext_l.split('.')[-1]
            self.letter_received.name = 'l_r' + '_' + str(
                self.id)+'_'+str(
                self.reference_invoice)+'.'+ext_l
        super(Invoice, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'

    def __str__(self):
        return self.reference_invoice


class InvoiceDetail(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    id_invoice = models.ForeignKey(Invoice,
                                   on_delete=models.CASCADE,
                                   related_name='rel_invoice_detail')
    id_product = models.ForeignKey(Products,
                                   on_delete=models.CASCADE,
                                   related_name='rel_product_detail', null=True)
    name_product = models.CharField(max_length=100, blank=False, null=False)
    description_product = models.CharField(max_length=200,
                                           blank=False,
                                           null=False)
    product_code = models.CharField(max_length=30, blank=False, null=True)
    unit_price = models.DecimalField(max_digits=13, decimal_places=2)
    quantity = models.IntegerField(null=True)
    total_price = models.DecimalField(max_digits=13, decimal_places=2)
    reference = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name = 'Invoice Detail'
        verbose_name_plural = 'Invoices Detail'

    def __str__(self):
        return self.id_invoice


class TransactionState(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                      auto_now=False,
                                      auto_now_add=True)
    name_state = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=500, null=True)

    class Meta:
        verbose_name = 'Transaction_state'
        verbose_name_plural = 'Transaction_states'

    def __str__(self):
        return self.name_state


class TypeTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    type_transaction = models.CharField(max_length=200, null=True)


class TransactionData(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                      auto_now=False,
                                      auto_now_add=True)
    quot = models.IntegerField(null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    num_aprob = models.CharField(max_length=100, blank=True, null=True)
    cod_reply = models.CharField(max_length=50, blank=True, null=True)
    messaje_reply = models.TextField(max_length=1000, blank=True, null=True)
    reference = models.CharField(max_length=200, null=False)
    total_tx = models.DecimalField(max_digits=13, decimal_places=2)
    num_recibo = models.CharField(max_length=100, blank=True, null=True)
    state = models.ForeignKey(TransactionState,
                              on_delete=models.CASCADE,
                              related_name='rel_state_tx', blank=True, null=True)
    type_transaction = models.ForeignKey(TypeTransaction,
                            on_delete=models.CASCADE,
                            related_name='rel_type_tx', blank=True, null=True)                        
    cuc = models.ForeignKey(ConfApiTransaction,
                            on_delete=models.CASCADE,
                            related_name='rel_con_tx', blank=True, null=True)                        
    tag_first_name = models.CharField(max_length=200, null=True)
    tag_last_name = models.CharField(max_length=200, null=True)
    tag_type_identification = models.ForeignKey(
        TypeIdentification, on_delete=models.CASCADE, related_name='rel_typeidenti_invoice_tr', null=True)
    tag_number_identification = models.CharField(max_length=200, null=True)
    tag_email = models.CharField(max_length=200, null=True)
    tag_cellphone = models.CharField(max_length=200, null=True)
    tag_desc_selling = models.TextField(max_length=1000, blank=True, null=True)
    tag_invoice_number_ext = models.CharField(max_length=200, null=True)
    tag_tax_iva = models.ForeignKey(
        PaymentPercentages, on_delete=models.CASCADE, related_name='rel_tax_iva', null=True)
    tag_store = models.ForeignKey(
        Stores, on_delete=models.CASCADE, related_name='rel_store_tx', null=True)
    

class TrxInf(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                  auto_now=False,
                                  auto_now_add=True)
    field = models.CharField(max_length=200, null=True)
    tx = models.ForeignKey(TransactionData,
                            on_delete=models.CASCADE,
                            related_name='rel_inf_tx', blank=True, null=True)                        

class TransactionCancelData(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                      auto_now=False,
                                      auto_now_add=True)
    transaction_id = models.ForeignKey(TransactionData,
                                       on_delete=models.CASCADE,
                                       related_name='rel_tx', blank=True, null=True)
    num_aprob = models.CharField(max_length=100, blank=True, null=True)
    num_recibo = models.CharField(max_length=100, blank=True, null=True)
    messaje_reply = models.TextField(max_length=1000, blank=True, null=True)
    date_chanel_tx = models.CharField(max_length=100, blank=True, null=True)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)
    email_plaintext_message = reset_password_token.key

    html_message = loader.render_to_string(
        'mails//restore_password.html',
        {
            'web_url': settings.WEB_URL,
            'token': email_plaintext_message,
        }
    )

    send_mail("Restaurar contraseña Kompralo", "Restaurar contraseña Kompralo", "noreply@somehost.local",
              [reset_password_token.user.email], fail_silently=True, html_message=html_message)


class TransferState(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                      auto_now=False,
                                      auto_now_add=True)
    name_state = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=500, null=True)

    class Meta:
        verbose_name = 'Transfer_state'
        verbose_name_plural = 'Transfer_states'

    def __str__(self):
        return self.name_state


class Transfers(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                      auto_now=False,
                                      auto_now_add=True)
    reference = models.CharField(max_length=200, null=True)
    account_number = models.CharField(max_length=200, null=True)
    responsible = models.CharField(max_length=200, null=True)
    val_request = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    val_transfer = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    val_commision_bank = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    val_commision_transfe = models.DecimalField(
        max_digits=13, decimal_places=2, null=True)
    bank = models.ForeignKey(
        Banks, on_delete=models.CASCADE, related_name='rel_bank_trans', null=True)
    typeaccount = models.ForeignKey(
        TypeAccount, on_delete=models.CASCADE, related_name='rel_typeaccount_trans', null=True)
    store = models.ForeignKey(
        Stores, on_delete=models.CASCADE, related_name='rel_store_trans', null=True)
    state = models.ForeignKey(
        TransferState, on_delete=models.CASCADE, related_name='rel_state_trans', null=True)

    class Meta:
        verbose_name = 'Transfer'
        verbose_name_plural = 'Transfers'

    def __str__(self):
        return self.id

class Binnacle(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField('creation date',
                                      auto_now=False,
                                      auto_now_add=True)
    observation = models.TextField(max_length=1000, blank=True, null=True)
    id_invoice = models.ForeignKey(Invoice,
                                   on_delete=models.CASCADE,
                                   related_name='rel_invoice_binnacle')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='rel_user_binnacle')
    check_binnacle = models.BooleanField('Check Binnacle p', default=False)
    check_binnacle_adm = models.BooleanField('Check Binnacle adm', default=False)