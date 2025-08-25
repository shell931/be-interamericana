from django.urls import path
from api.views.binnacles import BinnaclesCheckReturnViewSet
from rest_framework import routers
from django.conf.urls import include
from .views import *
from .views.invoice import PaymentWebhookViewSet
from django.conf.urls import url
from django.views.generic import TemplateView


router = routers.DefaultRouter()
"""CONFIG ROUTES"""
router.register('users', UserViewSet)
router.register('users-create', CreateUserViewSet, basename='user')
router.register('group', GroupViewSet)
router.register('menus', MenuViewSet)
router.register('group-list', GroupListViewSet)
router.register('departments', DepartmentsViewSet)
router.register('cities', CitiesViewSet)
"""ADMIN ROUTES"""
router.register('products', ProductsViewSet)
router.register('product_delete', ProductDeleteViewSet)
router.register('categories', CategoriesViewSet)
router.register('subcategories', SubCategoriesViewSet)
router.register('find_category_by_subcategory',
                FindCategoryBySubcategoryViewSet)
router.register('store', StoresViewSet)
router.register(r'user_group', UpdateGroupUserViewSet, basename='user_group')
router.register(r'user_group_edit', UpdateUserViewSet, basename='user_group_edit')

router.register('store_update', StoreUpdateViewSet)
router.register('images', ImagesViewSet)
router.register('product_store', ProductsNavStoreViewSet)
router.register('view/product_store', ProductsNavStoreView)
router.register(r'store_front',
                StoreNavStoreViewSet, basename='store_front')
router.register(r'update_percentage_store',
                UpdatePercentagesStoreViewSet, basename='update_percentage_store')
router.register(r'validate_user',
                ValidateUserExist, basename='validate_user')
router.register(r'payment_percentages_sale',
                PaymentPercentagesSaleViewSet, basename='payment_percentages_sale')
router.register(r'percentages_tax',
                PercentagesTaxViewSet, basename='percentages_tax')            
router.register(r'payment_percentages_payment',
                PaymentPercentagesPaymentViewSet, basename='payment_percentages_payment')
router.register('store_products_front', ProductsFrontStoreViewSet)
router.register(r'admin_products', AdminProductsViewSet, basename='tasks')
router.register(r'verify_stock_products',
                VerifyStockProductsViewSet, basename='tasks')
router.register('product_confirm', ProductsConfirmViewSet)
router.register('product_filter', SearchProductViewSet)
router.register('location_client', LocationClientViewSet)
router.register('user_front', UserFrontViewSet)
router.register('user_type', UserTypeViewSet)
router.register('type_identifier_front', TypeIdentifiersFrontViewSet)
router.register('invoice_header',  InvoiceHeaderViewSet)
router.register('invoice_detail', InvoiceDetailViewSet)

router.register('invoice_process_status', InvoiceInProcesReturnViewSet)

router.register('departments_front', DepartmentsFrontViewSet)
router.register('cities_front', CitiesFrontViewSet)
router.register('delete_product_image', ProductDeleteImageViewSet)
router.register('store_categories', StoreCategoriesViewSet)
router.register(r'store_documents', StoreDocumentsDataViewSet,
                basename='store_documents')
router.register(r'data_autentication_gateway', AutenticationDataGatewayViewSet,
                basename='data_autentication_gateway')
router.register(r'check_invoice', GetCheckInvoiceViewSet,
                basename='check_invoice')


router.register(r'bank_accounts', BankAccountsViewSet,
                basename='bank_accounts')
router.register(r'user_store', UserStoreViewSet,
                basename='user_store')
router.register(r'get_user', UserByIdViewSet,
                basename='get_user')
router.register(r'last_image', GetLatestImageViewSet,
                basename='last_image')

router.register(r'update_stock', UpdateStockViewSet,
                basename='update_stock')
router.register(r'update_status_invoice', UpdateStatusInvoiceViewSet,
                basename='update_status_invoice')

router.register(r'update_shippingvoucher_invoice', UpdateShippingVoucherViewSet,
                basename='update_shippingvoucher_invoice')

router.register(r'update_letterreceived_invoice', UpdateLetterReceivedViewSet,
                basename='update_letterreceived_invoice')

router.register(r'update_checkvalidation_invoice', UpdateCheckCallControllInvoiceViewSet,
                basename='update_checkvalidation_invoice')

router.register(r'update_checkrecord_invoice', UpdateCheckRecordnvoiceViewSet,
                basename='update_checkrecord_invoice')

router.register(r'update_checkshipment_invoice', UpdateCheckShipmentInvoiceViewSet,
                basename='update_checkshipment_invoice')

router.register(r'update_checkfinaly_invoice', UpdateCheckFinalyInvoiceViewSet,
                basename='update_checkfinaly_invoice')                
                            

router.register(r'count_image_prod', GetCountImageProductViewSet,
                basename='count_image_prod')

router.register(r'load_images', LoadImageProductsViewSet,
                basename='load_images')
router.register(r'delete_images', DeleteImageProductsViewSet,
                basename='delete_images')

"""NAVEGATION FRONT WEB ROUTES"""
router.register(r'locations_by_user',
                LocationClientByUserViewSet, basename='locations')
router.register(r'locations_by_id', LocationClientByIdViewSet,
                basename='locations_id')
router.register(r'location_client_checkout',
                LocationCheckoutClientViewSet, basename='locations_id')
router.register('general_update_location', LocationGeneralUpdatesViewSet)
router.register(r'products_categories',
                ProducsCategoriesViewSet, basename='prodcat')
router.register('product_subcategory', ProductSubcategoryNavStoreViewSet)
router.register(r'category_store', CategoriesStoreViewSet,
                basename='category_store')

router.register(r'society_type', SocietyTypeViewSet, basename='society_type')
router.register(r'banks', BanksViewSet, basename='banks')
router.register(r'type_accounts', TypeAccountViewSet, basename='type_accounts')
router.register(r'store_complete_data', StoreCompleteData,
                basename='store_complete_data')
router.register(r'store_by_category_data', StoreByCategoryData,
                basename='store_by_category_data')
router.register(r'set_transaction', TrancsactionCheckoutViewSet,
                basename='set_transaction')

router.register(r'exportable_transaction', ExportableTransactionViewSet,
                basename= 'exportable_transaction')

router.register(r'get_all_transactions',
                GetAllTransactionsViewSet, basename='get_all_transactions')

router.register(r'set_transaction_core', TrancsactionCoreViewSet,
                basename='set_transaction_core')

router.register(r'list_invoice', ListInvoiceViewSet, basename='list_invoice')

router.register(r'create_product', CreateProductViewSet,
                basename='create_product')
router.register(r'membership_request', MembershipRequest,
                basename='membership_request')
router.register(r'load_documents', LoadDocumentsViewSet,
                basename='load_documents')
router.register(r'load_logo', LoadLogoViewSet,
                basename='load_logo')
router.register(r'invoice_by_store', InvoiceByStoreViewSet,
                basename='invoice_by_store')
router.register(r'list_user_invoice', ListInvoiceUserViewSet,
                basename='list_user_invoice')
router.register(r'list_user_invoice_detail',
                ListInvoiceDetailUserViewSet, basename='list_user_invoice_detail')
router.register(r'bank_accounts_save', BankAccountsSaveViewSet,
                basename='bank_accounts_save')

router.register(r'cancel_transaction', CancelTransactionViewSet,
                basename='cancel_transaction')

router.register(r'contra_transaction', ContraTransactionViewSet,
                basename='contra_transaction')

router.register(r'get_balance_account',
                GetBalanceAccountViewSet, basename='get_balance_account')
router.register(r'get_balance_detail_account',
                GetBalanceDetailTransactionViewSet, basename='get_balance_detail_account')                

router.register(r'get_transfer_data',
                GetTransferDataViewSet, basename='get_transfer_data')

router.register(r'get_transfer_detail_data',
                GetTransferDetailViewSet, basename='get_transfer_detail_data')

router.register(r'send_email_store_creation_request', sendEmailStoreRequestViewSet,
                basename='send_email_store_creation_request')

router.register(r'send_email_rejection_transaction_customer', sendEmailRejectionTransactionCustomerViewSet,
                basename='send_email_rejection_transaction_customer') 

router.register(r'send_customer_store_email', sendCustomerStoreEmailViewSet,
                basename='send_customer_store_email') 

router.register(r'send_seller_store_email', sendSellerEmailViewSet,
                basename='send_seller_store_email') 


router.register(r'send_email_welcome_store', sendEmailWelcomeStoreViewSet,
                basename='send_email_welcome_store') 


router.register(r'get_transaction_by_store', GetTransactionsByStoreViewSet,
                basename='get_transaction_by_store') 

router.register(r'get_transaction_by_id', GetTransactionsByIdViewSet,
                basename='get_transaction_by_id') 
 

router.register(r'get_all_transfer_data',
                GetAllTransfersDataViewSet, basename='get_all_transfer_data')
                
router.register(r'transfer_request', TransferRequestViewSet,
                basename='transfer_request')                

router.register(r'status_transfer', UpdateStatusTransferViewSet,
                basename='status_transfer')

router.register(r'set_assisted_selling', SetAssitedSelling,
                basename='set_assisted_selling')

router.register(r'send_email_rejection_transaction', sendEmailRejectionTransactionCustomerViewSet,
                basename='send_email_rejection_transaction')

router.register(r'send_email_transfer_request', sendEmailTransferRequestViewSet,
                basename='send_email_transfer_request')

router.register(r'send_email_reply_transfer', sendEmailReplyTransferViewSet,
                basename='send_email_reply_transfer')

router.register(r'get_con_api_data',
                GetConfApiTransactionViewSet, basename='get_con_api_data')

router.register(r'list_binnacles',
                GetListBinnacles, basename='list_binnacles')

router.register(r'create_binnacle',
                CreateBinnacles, basename='create_binnacle')


router.register('get_binnacle_number', GetListBinnaclesNumber,
                basename='get_binnacle_number')

urlpatterns = [
    path('', include(router.urls)),
    path('payment-webhook/', PaymentWebhookViewSet.as_view({'post': 'create'}), name='payment_webhook'),
    path('password_reset_market/', include('django_rest_passwordreset.urls',
                                           namespace='password_reset_market')),
]
