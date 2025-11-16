from api.models import Domain, Tenant, User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django_tenants.admin import TenantAdminMixin


@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
        list_display = ('name', 'schema_name', 'paid_until', 'on_trial')


@admin.register(Domain)
class DomainAdmin(TenantAdminMixin, admin.ModelAdmin):
        list_display = ('domain', 'tenant', 'is_primary')

# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     pass


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'tenant', 'is_superuser', 'is_staff')
    list_filter = ('tenant', 'is_superuser', 'is_staff')
    search_fields = ('username', 'email')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(tenant=request.user.tenant)