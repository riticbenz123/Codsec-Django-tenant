from django.contrib import admin
from tenant_data.models import TenantData,Product,Product_Batch

# Register your models here.
admin.site.register(TenantData)
admin.site.register(Product)
admin.site.register(Product_Batch)