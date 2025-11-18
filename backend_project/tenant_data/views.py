import datetime
from decimal import Decimal

from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (Product, Product_Batch, Purchase, PurchaseItem, Sale,
                     SalesItem, TenantData)
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


class SaleCreateView(APIView):
    def post(self, request):
        serializer = SaleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseCreateView(APIView):
    def post(self, request):
        serializer = PurchaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

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
    
    
    
class StockLedgerView(APIView):
    def get(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not start_date_str or not end_date_str:
            return Response({"error": "start_date and end_date are required"}, status=status.HTTP_400_BAD_REQUEST)

        start_date = parse_datetime(start_date_str)
        end_date = parse_datetime(end_date_str) + datetime.timedelta(days=1) - datetime.timedelta(seconds=1) 

        if not start_date or not end_date:
            return Response({"error": "Invalid date format. Use ISO format like 2025-11-01T00:00:00Z"}, status=status.HTTP_400_BAD_REQUEST)

        products = Product.objects.all()
        ledger = []
        for product in products:
            opening_qty = Decimal('0')
            opening_total_cost = Decimal('0')
            opening_total_selling = Decimal('0')
            batches = product.product_batch_set.filter(added_date__lt=start_date)
            for batch in batches:
                sales_after = batch.sales_items.filter(sale__created_at__gte=start_date).aggregate(total=Sum('quantity'))['total'] or 0
                qty_at_open = batch.quantity + sales_after
                opening_qty += qty_at_open
                opening_total_cost += qty_at_open * batch.cost_rate
                opening_total_selling += qty_at_open * batch.selling_rate
            opening_avg_cost = opening_total_cost / opening_qty if opening_qty > 0 else Decimal('0')
            opening_avg_selling = opening_total_selling / opening_qty if opening_qty > 0 else Decimal('0')
            opening = {
                'quantity': opening_qty,
                'avg_cost_price': opening_avg_cost,
                'avg_selling_price': opening_avg_selling
            }

            purchase_items = PurchaseItem.objects.filter(
                purchase__purchase_date__gte=start_date,
                purchase__purchase_date__lte=end_date,
                product_batch__product=product
            )
            purchase_qty = purchase_items.aggregate(total=Sum('quantity'))['total'] or Decimal('0')
            purchase_total_cost = purchase_items.aggregate(total=Sum('total_cost_price'))['total'] or Decimal('0')
            purchase_total_selling = purchase_items.aggregate(total=Sum('total_selling_price'))['total'] or Decimal('0')
            purchase_avg_cost = purchase_total_cost / purchase_qty if purchase_qty > 0 else Decimal('0')
            purchase_avg_selling = purchase_total_selling / purchase_qty if purchase_qty > 0 else Decimal('0')
            purchases = {
                'quantity': purchase_qty,
                'avg_cost_price': purchase_avg_cost,
                'avg_selling_price': purchase_avg_selling
            }

            sales_items = SalesItem.objects.filter(
                sale__created_at__gte=start_date,
                sale__created_at__lte=end_date,
                product_batch__product=product
            )
            sales_qty = sales_items.aggregate(total=Sum('quantity'))['total'] or Decimal('0')
            sales_total_cost = sales_items.aggregate(total=Sum('total_cost_price'))['total'] or Decimal('0')
            sales_total_selling = sales_items.aggregate(total=Sum('total_selling_price'))['total'] or Decimal('0')
            sales_avg_cost = sales_total_cost / sales_qty if sales_qty > 0 else Decimal('0')
            sales_avg_selling = sales_total_selling / sales_qty if sales_qty > 0 else Decimal('0')
            sales = {
                'quantity': sales_qty,
                'avg_cost_price': sales_avg_cost,
                'avg_selling_price': sales_avg_selling
            }

            closing_qty = Decimal('0')
            closing_total_cost = Decimal('0')
            closing_total_selling = Decimal('0')
            batches = product.product_batch_set.filter(added_date__lte=end_date)
            for batch in batches:
                sales_after = batch.sales_items.filter(sale__created_at__gt=end_date).aggregate(total=Sum('quantity'))['total'] or 0
                qty_at_close = batch.quantity + sales_after
                closing_qty += qty_at_close
                closing_total_cost += qty_at_close * batch.cost_rate
                closing_total_selling += qty_at_close * batch.selling_rate
            closing_avg_cost = closing_total_cost / closing_qty if closing_qty > 0 else Decimal('0')
            closing_avg_selling = closing_total_selling / closing_qty if closing_qty > 0 else Decimal('0')
            closing = {
                'quantity': closing_qty,
                'avg_cost_price': closing_avg_cost,
                'avg_selling_price': closing_avg_selling
            }
            
            ledger.append({
                'product_name': product.name,
                'opening': opening,
                'purchases': purchases,
                'sales': sales,
                'closing': closing
            })

        return Response(ledger)
