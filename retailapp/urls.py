from django.urls import path
from retailapp import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add-customer/', views.register_customer, name='add_customer'),
    path('list-customers/', views.list_customers, name='list_customers'),
    path('product-purchase/', views.purchase_product, name='purchase_product'),
    path('customer/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customer/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customer/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('record-payment/', views.record_payment, name='record_payment'),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_inventory_item, name='add_inventory_item'),
    path('inventory/edit/<int:item_id>/', views.edit_inventory_item, name='edit_inventory_item'),
    path('inventory/delete/<int:item_id>/', views.delete_inventory_item, name='delete_inventory_item'),
    path('customers/<int:customer_id>/payments/', views.customer_payments_json, name='customer_payments_json'),
    path('customers/<int:customer_id>/purchases/', views.customer_purchases_json, name='customer_purchases_json'),
    path('create-exchange/<int:item_id>/', views.create_exchange_request, name='create_exchange_request'),
    path('review-exchange/<int:exchange_id>/', views.admin_review_exchange, name='admin_review_exchange'),
]