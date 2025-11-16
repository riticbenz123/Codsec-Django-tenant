from api.models import Domain, Tenant, User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django_tenants.admin import TenantAdminMixin


@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
        list_display = ('name', 'paid_until')


@admin.register(Domain)
class DomainAdmin(TenantAdminMixin, admin.ModelAdmin):
        pass

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass