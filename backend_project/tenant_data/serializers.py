from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from .models import *


class TenantDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantData
        fields = '__all__'


# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    batch_count = serializers.IntegerField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    total_cost_value = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total_selling_value = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('batch_count', 'total_quantity', 'total_cost_value', 'total_selling_value')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['batch_count'] = instance.batch_count()
        data['total_quantity'] = instance.total_quantity()
        data['total_cost_value'] = instance.total_cost_value()
        data['total_selling_value'] = instance.total_selling_value()
        return data


class ProductBatchSerializer(serializers.ModelSerializer):
    total_cost_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_selling_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Product_Batch
        fields = '__all__'
        read_only_fields = ('added_date', 'total_selling_price', 'total_cost_price')

    def validate(self, data):
        expiry = data.get('expiry_date')
        added = data.get('added_date') or getattr(self.instance, 'added_date', None)
        if expiry and added and expiry <= added:
            raise serializers.ValidationError("expiry_date must be after added_date.")
        return data

class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = ['product_name', 'batch_number', 'quantity']
        
class PurchaseSerializer(serializers.ModelSerializer):
    batch_number   = serializers.CharField(write_only=True)
    product_id     = serializers.PrimaryKeyRelatedField(
                        queryset=Product.objects.all(), write_only=True)
    expiry_date    = serializers.DateTimeField(write_only=True)
    cost_rate      = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True)
    selling_rate   = serializers.DecimalField(
                        max_digits=10, decimal_places=2, write_only=True, required=False, default=0)
    quantity       = serializers.IntegerField(min_value=1)  # Same quantity for batch & purchase
    cost_price     = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    supplier_name  = serializers.CharField(max_length=100)

    product_name   = serializers.CharField(source='product_batch.product.name', read_only=True)
    total_cost     = serializers.SerializerMethodField()
    batch_no = serializers.CharField(source='product_batch.batch_number', read_only=True)
    items = PurchaseItemSerializer(many=True, read_only=True)

    class Meta:
        model = Purchase
        fields = [
            'id', 'bill_no', 'batch_no',
            'batch_number', 'product_id', 'expiry_date',
            'quantity', 'cost_rate', 'selling_rate',
            'cost_price', 'supplier_name',
            'created_at', 'product_name', 'total_cost', 'items'
        ]
        read_only_fields = ['bill_no', 'created_at', 'product_name', 'total_cost', 'items']

    def get_total_cost(self, obj):
        return obj.quantity * obj.cost_price

    def validate(self, attrs):
        batch_number = attrs.pop('batch_number')
        product = attrs.pop('product_id')
        expiry_date = attrs.pop('expiry_date')
        quantity = attrs['quantity']
        cost_rate = attrs.pop('cost_rate')
        selling_rate = attrs.pop('selling_rate', Decimal('0.00'))

        if Product_Batch.objects.filter(batch_number=batch_number).exists():
            raise serializers.ValidationError({
                "batch_number": f"Batch '{batch_number}' already exists."
            })

        # batch = Product_Batch.objects.create(
        #     product=product,
        #     batch_number=batch_number,
        #     expiry_date=expiry_date,
        #     quantity=quantity,          
        #     cost_rate=cost_rate,
        #     selling_rate=selling_rate
        # )
        batch = Product_Batch(
            product=product,
            batch_number=batch_number,
            expiry_date=expiry_date,
            quantity=quantity,
            cost_rate=cost_rate,
            selling_rate=selling_rate
        )

        attrs['product_batch'] = batch
        if 'cost_price' not in attrs or attrs['cost_price'] in (None, 0, Decimal('0')):
            attrs['cost_price'] = cost_rate

        return attrs
    
class SalesItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesItem
        fields = ['product_name', 'batch_number', 'quantity']

class SaleSerializer(serializers.ModelSerializer):
    batch_number = serializers.CharField(write_only=True)
    batch_no = serializers.CharField(source='product_batch.batch_number', read_only=True)
    product_name = serializers.CharField(source='product_batch.product.name', read_only=True)
    total_selling = serializers.SerializerMethodField()
    items = SalesItemSerializer(many=True, read_only=True)
    class Meta:
        model = Sale
        fields = [
            'id', 'bill_no', 'batch_number', 'batch_no', 'quantity',
            'selling_price', 'customer_name', 'created_at',
            'product_name', 'total_selling', 'items'
        ]
        read_only_fields = ['bill_no', 'created_at', 'product_name', 'total_selling', 'batch_no', 'items']

    def get_total_selling(self, obj):
        return obj.quantity * obj.selling_price

    def validate(self, attrs):
        batch_number = attrs.pop('batch_number')
        try:
            batch = Product_Batch.objects.get(batch_number=batch_number)
        except Product_Batch.DoesNotExist:
            raise serializers.ValidationError({"batch_number": "Batch not found."})

        attrs['product_batch'] = batch
        if 'selling_price' not in attrs or not attrs['selling_price']:
            attrs['selling_price'] = batch.selling_rate
        else:
            try:
                attrs['selling_price'] = Decimal(str(attrs['selling_price']))
            except:
                raise serializers.ValidationError({"selling_price": "Must be a valid decimal."})

        requested = attrs['quantity']
        # sold_so_far = batch.sales.aggregate(s=Sum('quantity'))['s'] or 0
        
        # available = batch.quantity - sold_so_far
        available = batch.quantity
        
        if requested > available:
            raise serializers.ValidationError(
                f"Only {available} units left in batch {batch_number}."
            )
        return attrs