from django.db.models.functions import Upper
from django.http import JsonResponse
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
        
    def validate_name(self, value):
        if not value:
            return value
        upper_value = value.upper()
        qs = Product.objects.annotate(upper_name=Upper('name')).filter(upper_name=upper_value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            return JsonResponse({"success": False, "message": "A product with this name already exists."},status=400)
        return value

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

    def validate_batch_number(self, value):

        if not value or value.strip() == "":
            return value

        upper_batch = str(value).strip().upper()

        queryset = Product_Batch.objects.exclude(batch_number__isnull=True) \
                                        .exclude(batch_number__exact='') \
                                        .annotate(upper_batch=Upper('batch_number')) \
                                        .filter(upper_batch=upper_batch)

        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "A batch with this batch number already exists."
            )
        return value

    def validate(self, attrs):
        expiry = attrs.get('expiry_date')
        added_date = attrs.get('added_date') or (
            self.instance.added_date if self.instance else None
        )
        if expiry and added_date and expiry <= added_date:
            raise serializers.ValidationError(
                "Expiry date must be after the added date."
            )
        return attrs


class PurchaseItemCreateSerializer(serializers.Serializer):
    batch_number = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    product_id = serializers.IntegerField()
    expiry_date = serializers.DateTimeField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1)
    cost_rate = serializers.DecimalField(max_digits=10, decimal_places=2)
    selling_rate = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        product_id = data.get('product_id')
        if product_id is None:
            raise serializers.ValidationError("product_id is required")
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product_id")
        if product.expirable:
            if 'batch_number' not in data or not data['batch_number']:
                raise serializers.ValidationError({"batch_number": "This field is required for expirable products."})
            if 'expiry_date' not in data or data['expiry_date'] is None:
                raise serializers.ValidationError({"expiry_date": "This field is required for expirable products."})
        else:
            data['batch_number'] = None
            data['expiry_date'] = None
        return data

class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = ['id', 'product_name', 'batch_number', 'cost_rate', 'selling_rate', 'quantity', 'total_selling_price', 'total_cost_price']

class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Purchase
        fields = ['bill_no', 'supplier_name', 'purchase_date', 'total_amount', 'notes', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        validated_data.pop('total_amount', None) 
        purchase = Purchase.objects.create(**validated_data)
        total = 0
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            batch = Product_Batch.objects.create(
                product=product,
                batch_number=item_data['batch_number'],
                expiry_date=item_data['expiry_date'],
                quantity=item_data['quantity'],
                selling_rate=item_data['selling_rate'],
                cost_rate=item_data['cost_rate'],
            )
            purchase_item = PurchaseItem.objects.create(
                purchase=purchase,
                product_batch=batch,
                product_name=product.name,
                batch_number=batch.batch_number,
                cost_rate=item_data['cost_rate'],
                selling_rate=item_data['selling_rate'],
                quantity=item_data['quantity'],
            )
            total += purchase_item.total_cost_price
        purchase.total_amount = total
        purchase.save()
        return purchase

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['items'] = PurchaseItemSerializer(instance.items.all(), many=True).data
        return ret

class SalesItemCreateSerializer(serializers.Serializer):
    batch_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class SalesItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesItem
        fields = ['id', 'product_name', 'batch_number', 'cost_rate', 'selling_rate', 'quantity', 'total_selling_price', 'total_cost_price']

class SaleSerializer(serializers.ModelSerializer):
    items = SalesItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Sale
        fields = ['bill_no', 'customer_name', 'total_amount', 'quantity', 'notes', 'items']
        extra_kwargs = {
            'total_amount': {'read_only': True},
            'quantity': {'read_only': True}
        }

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        sale = Sale.objects.create(quantity=0, **validated_data)
        total_amount = 0
        total_quantity = 0
        for item_data in items_data:
            try:
                batch = Product_Batch.objects.get(id=item_data['batch_id'])
                product = batch.product

            except Product_Batch.DoesNotExist:
                raise serializers.ValidationError(f"Batch with id {item_data['batch_id']} does not exist.")
            if item_data['quantity'] > batch.quantity:
                raise serializers.ValidationError(f"Insufficient quantity in batch {item_data['batch_id']}. Available: {batch.quantity}")            
            if not product.expirable:
                print(f"if run{batch.id}")
                sales_item = SalesItem.objects.create(
                    sale=sale,
                    product_batch=batch,
                    product_name=batch.product.name,
                    batch_number=None,
                    cost_rate=batch.cost_rate,
                    selling_rate=batch.selling_rate,
                    quantity=item_data['quantity'],
                )
            else:
                print( f"else run{batch.id}")
                sales_item = SalesItem.objects.create(
                    sale=sale,
                    product_batch=batch,
                    product_name=batch.product.name,
                    batch_number=batch.batch_number,
                    cost_rate=batch.cost_rate,
                    selling_rate=batch.selling_rate,
                    quantity=item_data['quantity'],
                )
            total_amount += sales_item.total_selling_price
            total_quantity += sales_item.quantity
            batch.quantity -= sales_item.quantity
            batch.save()
        sale.total_amount = total_amount
        sale.quantity = total_quantity
        sale.save()
        return sale

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['items'] = SalesItemSerializer(instance.items.all(), many=True).data
        return ret