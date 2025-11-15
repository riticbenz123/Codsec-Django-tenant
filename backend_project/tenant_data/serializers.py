from rest_framework import serializers

from .models import Product, Product_Batch, TenantData


class TenantDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantData
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductBatchSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Product_Batch
        fields = '__all__'
        read_only_fields = ('added_date', 'total_price')

    def validate(self, data):
        expiry = data.get('expiry_date')
        added = data.get('added_date') or getattr(self.instance, 'added_date', None)
        if expiry and added and expiry <= added:
            raise serializers.ValidationError("expiry_date must be after added_date.")
        return data