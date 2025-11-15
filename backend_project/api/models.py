from django.db import models
from django.contrib.auth.models import User
from django_tenants.models import TenantMixin, DomainMixin
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Tenant(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField()
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)

    auto_create_schema = True


class Domain(DomainMixin):
    pass


class User(AbstractUser):
    pass