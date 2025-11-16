from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


# Create your models here.
class Tenant(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField()
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)

    auto_create_schema = True


class Domain(DomainMixin):
    pass


# class User(AbstractUser):
#     pass

class User(AbstractUser):
    tenant = models.ForeignKey(
        Tenant,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='users'
    )

    def __str__(self):
        return self.username

    @property
    def is_tenant_admin(self):
        return self.is_staff and self.tenant is not None

    # class Meta:
    #     db_table = 'public"."auth_user'