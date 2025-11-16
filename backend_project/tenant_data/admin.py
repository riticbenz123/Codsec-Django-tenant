# admin.py
from django.contrib import admin
from django.db.models import Count, Sum
from tenant_data.models import Product, Product_Batch, TenantData


@admin.register(TenantData)
class TenantDataAdmin(admin.ModelAdmin):
    pass   


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'product_type',
        'batch_count',          
        'total_quantity',       
        'total_cost_value',     
        'total_selling_value',  
    )
    search_fields = ('name', 'product_type')
    readonly_fields = (
        'batch_count',
        'total_quantity',
        'total_cost_value',
        'total_selling_value',
    )
    def batch_count(self, obj):
        return obj.batch_count()
    batch_count.short_description = "Number of Batches"

    def total_quantity(self, obj):
        return obj.total_quantity()
    total_quantity.short_description = "Total Quantity"

    def total_cost_value(self, obj):
        return obj.total_cost_value()
    total_cost_value.short_description = "Total Cost Value"

    def total_selling_value(self, obj):
        return obj.total_selling_value()
    total_selling_value.short_description = "Total Selling Value"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _batch_count=Count('product_batch'),
            _total_quantity=Sum('product_batch__quantity'),
            _total_cost_price=Sum('product_batch__total_cost_price'),
            _total_selling_price=Sum('product_batch__total_selling_price'),
        )

    def batch_count(self, obj):
        return getattr(obj, '_batch_count', None) or obj.batch_count()
    def total_quantity(self, obj):
        return getattr(obj, '_total_quantity', None) or obj.total_quantity()
    def total_cost_value(self, obj):
        return getattr(obj, '_total_cost_price', None) or obj.total_cost_value()
    def total_selling_value(self, obj):
        return getattr(obj, '_total_selling_price', None) or obj.total_selling_value()
    
    
@admin.register(Product_Batch)
class ProductBatchAdmin(admin.ModelAdmin):
    list_display = (
        'batch_number',
        'product',
        'added_date',
        'expiry_date',
        'quantity',
        'cost_rate',
        'selling_rate',
        'total_cost_price',
        'total_selling_price',
    )
    list_filter = ('product', 'added_date')
    search_fields = ('batch_number', 'product__name')
    readonly_fields = ('added_date', 'total_cost_price', 'total_selling_price')