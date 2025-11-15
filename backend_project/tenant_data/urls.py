from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.product_list_create, name='product-list'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),
    
    path('batches/', views.batch_list_create, name='batch-list'),
    path('batches/<int:pk>/', views.batch_detail, name='batch-detail'),
    
    path('tenantdata/', views.tenantdata_list_create, name='tenantdata-list'),
    path('tenantdata/<int:pk>/', views.tenantdata_detail, name='tenantdata-detail')
]