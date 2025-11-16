from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Product, Product_Batch, Purchase, Sale, TenantData
from .serializers import (ProductBatchSerializer, ProductSerializer,
                          PurchaseSerializer, SaleSerializer,
                          TenantDataSerializer)


# Create your views here.
def get_tenant(request):
    return getattr(request, 'tenant', None)

@api_view(['GET', 'POST'])
def product_list_create(request):
    print("reached")
    tenant = get_tenant(request)
    if not tenant:
        return Response({"error": "Tenant not resolved"}, status=400)

    if request.method == 'GET':
        qs = Product.objects.all()
        ser = ProductSerializer(qs, many=True)
        return Response(ser.data)

    if request.method == 'POST':
        ser = ProductSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    tenant = get_tenant(request)
    if not tenant:
        return Response({"error": "Tenant not found"}, status=400)

    try:
        obj = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductSerializer(obj)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProductSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def batch_list_create(request):
    tenant = get_tenant(request)
    if not tenant:
        return Response({"error": "Tenant not found"}, status=400)

    if request.method == 'GET':
        items = Product_Batch.objects.all()
        serializer = ProductBatchSerializer(items, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductBatchSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def batch_detail(request, pk):
    tenant = get_tenant(request)
    if not tenant:
        return Response({"error": "Tenant not found"}, status=400)

    try:
        obj = Product_Batch.objects.get(pk=pk)
    except Product_Batch.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductBatchSerializer(obj)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProductBatchSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def create_sale(request):
    tenant = get_tenant(request)
    if not tenant:
        return Response({"error": "Tenant not found"}, status=400)

    data = request.data
    if isinstance(data, dict):
        items = [data]
    elif isinstance(data, list):
        items = data
    else:
        return Response({"error": "Expected a JSON object or array."}, status=400)
    created_sales = []
    errors = []
    with transaction.atomic():
        for index, item in enumerate(items):
            item_copy = item.copy()
            serializer = SaleSerializer(data=item_copy, context={'request': request})
            
            if serializer.is_valid():
                sale = serializer.save()
                created_sales.append(SaleSerializer(sale).data)
            else:
                errors.append({f"item_{index}": serializer.errors})
        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
    return Response(created_sales, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def show_all_sale(request):
    tenant = get_tenant(request)
    if not tenant:
        return Response({"error": "Tenant not found"}, status=400)
    
    sales = Sale.objects.select_related('product_batch__product').all()
    serializer = SaleSerializer(sales, many=True)
    return Response(serializer.data)



# @api_view(['POST'])
# def create_purchase(request):
#     tenant = get_tenant(request)
#     if not tenant:
#         return Response({"error": "Tenant not found"}, status=400)
#     data = request.data.copy()
#     batch_number = data.get('batch_number', None)
#     if not batch_number:
#         return Response({"batch_number": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
#     serializer = PurchaseSerializer(data=data, context={'request': request})
#     if serializer.is_valid():
#         purchase = serializer.save()
#         return Response(PurchaseSerializer(purchase).data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_purchase(request):
    tenant = get_tenant(request)
    if not tenant:
        return Response({"error": "Tenant not found"}, status=400)

    data = request.data
    if isinstance(data, dict):
        items = [data]
    elif isinstance(data, list):
        items = data
    else:
        return Response({"error": "Expected a JSON object or array."},status=status.HTTP_400_BAD_REQUEST)

    created = []
    errors  = []

    with transaction.atomic():
        for idx, item in enumerate(items):
            item_copy = item.copy()
            serializer = PurchaseSerializer(data=item_copy,context={'request': request})
            if serializer.is_valid():
                batch = serializer.validated_data.pop('product_batch')
                batch.save()
                purchase = Purchase(**serializer.validated_data)
                purchase.product_batch = batch
                purchase.save() 
                created.append(PurchaseSerializer(purchase).data)
            else:
                errors.append({f"item_{idx}": serializer.errors})
        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
    return Response(created, status=status.HTTP_201_CREATED)



@api_view(['GET'])
def show_all_purchases(request):
    tenant = get_tenant(request)
    if not tenant:
        return Response({"error": "Tenant not found"}, status=400)
    purchases = Purchase.objects.select_related('product_batch__product').all()
    serializer = PurchaseSerializer(purchases, many=True)
    return Response(serializer.data)
    

@api_view(['GET', 'POST'])
def tenantdata_list_create(request):
    tenant = get_tenant(request)
    if not tenant:
        return Response({"error": "Tenant not resolved"}, status=400)

    if request.method == 'GET':
        qs = TenantData.objects.all()
        ser = TenantDataSerializer(qs, many=True)
        return Response(ser.data)

    if request.method == 'POST':
        ser = TenantDataSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'PUT', 'DELETE'])
def tenantdata_detail(request, pk):
    tenant= get_tenant(request)
    if not tenant:
        return Response({"error":"Tenant not resolved"}, status =400)
    
    try:
        obj = TenantData.objects.get(pk=pk)
    except:
        return Response(status = status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = TenantDataSerializer(obj)
        return Response(serializer.data)
    
    if request.method == 'PUT':
        serializer = TenantDataSerializer(obj, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
