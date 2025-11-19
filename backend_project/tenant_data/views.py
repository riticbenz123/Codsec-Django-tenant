import datetime
from decimal import Decimal

from django.db.models import Sum
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *


# Create your views here.
def get_tenant(request):
    return getattr(request, 'tenant', None)

class ProductListCreateView(APIView):
    def get(self, request):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not resolved"}, status=400)
        qs = Product.objects.all()
        ser = ProductSerializer(qs, many=True)
        return Response({"success":True, "data": ser.data}, status=status.HTTP_200_OK)

    def post(self, request):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not resolved"}, status=400)
        ser = ProductSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response({"success":True, "message": "Product Created Successfully"}, status=status.HTTP_201_CREATED)
        return Response({"success": False,"errors": ser.errors }, status=status.HTTP_400_BAD_REQUEST)



class ProductDetailView(APIView):
    def get(self, request, pk):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not found"}, status=400)
        try:
            obj = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"success":False, "message":"Product not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(obj)
        return Response({"success":True, "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not found"}, status=400)
        try:
            obj = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"success":False, "message":"Product not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success":True, "message":"Product Updated", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False,"errors": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not found"}, status=400)
        try:
            obj = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"success":False, "message":"Product not found"},status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({"success":True, "message":"Product Deleted Successfully"},status=status.HTTP_204_NO_CONTENT)


class BatchListCreateView(APIView):
    def get(self, request):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not found"}, status=400)
        items = Product_Batch.objects.all()
        serializer = ProductBatchSerializer(items, many=True)
        return Response({"success":True, "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not found"}, status=400)
        serializer = ProductBatchSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success":True, "message": "Product Batch Created Successfully"}, status=status.HTTP_201_CREATED)
        return Response({"success": False,"errors": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

class BatchDetailView(APIView):
    def get(self, request, pk):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not found"}, status=400)
        try:
            obj = Product_Batch.objects.get(pk=pk)
        except Product_Batch.DoesNotExist:
            return Response({"success":False, "message":"Product Batch not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = ProductBatchSerializer(obj)
        return Response({"success":True, "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not found"}, status=400)
        try:
            obj = Product_Batch.objects.get(pk=pk)
        except Product_Batch.DoesNotExist:
            return Response({"success":False, "message":"Product Batch not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = ProductBatchSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success":True, "message":"Product Batch Updated", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False,"errors": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not found"}, status=400)
        try:
            obj = Product_Batch.objects.get(pk=pk)
        except Product_Batch.DoesNotExist:
            return Response({"success":False, "message":"Product Batch not found"},status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({"success":True, "message":"Product Batch Deleted Successfully"},status=status.HTTP_204_NO_CONTENT)


class SaleView(APIView):
    def get(self, request):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not resolved"}, status=400)
        qs = Sale.objects.all()
        ser = SaleSerializer(qs, many=True)
        return Response({"success":True, "data": ser.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = SaleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success":True, "message":"Sale Created Successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False,"errors": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)



class PurchaseView(APIView):
    def get(self, request):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not resolved"}, status=400)
        qs = Purchase.objects.all()
        ser = PurchaseSerializer(qs, many=True)
        return Response({"success":True, "data": ser.data}, status=status.HTTP_200_OK)

    
    def post(self, request):
        serializer = PurchaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success":True, "message":"Purchase Created Successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False,"errors": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

class TenantDataListCreateView(APIView):
    def get(self, request):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not resolved"}, status=400)
        qs = TenantData.objects.all()
        ser = TenantDataSerializer(qs, many=True)
        return Response(ser.data)

    def post(self, request):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not resolved"}, status=400)
        ser = TenantDataSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class TenantDataDetailView(APIView):
    def get(self, request, pk):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not resolved"}, status=400)
        try:
            obj = TenantData.objects.get(pk=pk)
        except TenantData.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TenantDataSerializer(obj)
        return Response(serializer.data)

    def put(self, request, pk):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not resolved"}, status=400)
        try:
            obj = TenantData.objects.get(pk=pk)
        except TenantData.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TenantDataSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        tenant = get_tenant(request)
        if not tenant:
            return Response({"error": "Tenant not resolved"}, status=400)
        try:
            obj = TenantData.objects.get(pk=pk)
        except TenantData.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
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

        return Response({"success":True, "data":ledger})
    
    
class StockLedgerSeparatedView(APIView):
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
        openings_list = []
        purchases_list = []
        sales_list = []
        closings_list = []

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
            if opening_qty > 0:
                opening_avg_cost = opening_total_cost / opening_qty
                opening_avg_selling = opening_total_selling / opening_qty
                openings_list.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'quantity': opening_qty,
                    'avg_cost_price': opening_avg_cost,
                    'avg_selling_price': opening_avg_selling
                })

  
            purchase_items = PurchaseItem.objects.filter(
                purchase__purchase_date__gte=start_date,
                purchase__purchase_date__lte=end_date,
                product_batch__product=product
            )
            purchase_qty = purchase_items.aggregate(total=Sum('quantity'))['total'] or Decimal('0')
            if purchase_qty > 0:
                purchase_total_cost = purchase_items.aggregate(total=Sum('total_cost_price'))['total'] or Decimal('0')
                purchase_total_selling = purchase_items.aggregate(total=Sum('total_selling_price'))['total'] or Decimal('0')
                purchase_avg_cost = purchase_total_cost / purchase_qty
                purchase_avg_selling = purchase_total_selling / purchase_qty
                purchases_list.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'quantity': purchase_qty,
                    'avg_cost_price': purchase_avg_cost,
                    'avg_selling_price': purchase_avg_selling
                })

      
            sales_items = SalesItem.objects.filter(
                sale__created_at__gte=start_date,
                sale__created_at__lte=end_date,
                product_batch__product=product
            )
            sales_qty = sales_items.aggregate(total=Sum('quantity'))['total'] or Decimal('0')
            if sales_qty > 0:
                sales_total_cost = sales_items.aggregate(total=Sum('total_cost_price'))['total'] or Decimal('0')
                sales_total_selling = sales_items.aggregate(total=Sum('total_selling_price'))['total'] or Decimal('0')
                sales_avg_cost = sales_total_cost / sales_qty
                sales_avg_selling = sales_total_selling / sales_qty
                sales_list.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'quantity': sales_qty,
                    'avg_cost_price': sales_avg_cost,
                    'avg_selling_price': sales_avg_selling
                })

 
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
            if closing_qty > 0:
                closing_avg_cost = closing_total_cost / closing_qty
                closing_avg_selling = closing_total_selling / closing_qty
                closings_list.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'quantity': closing_qty,
                    'avg_cost_price': closing_avg_cost,
                    'avg_selling_price': closing_avg_selling
                })

        # return Response({
        #     'openings': openings_list,
        #     'purchases': purchases_list,
        #     'sales': sales_list,
        #     'closings': closings_list
        # })
        
        return Response({"success":True, "data":{
            'openings': openings_list,
            'purchases': purchases_list,
            'sales': sales_list,
            'closings': closings_list
        }})
        