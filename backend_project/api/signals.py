# api/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_tenants.utils import get_public_schema_name, schema_context
from django.db import connection  # ← This is correct
from .models import User, Tenant
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def sync_tenant_user_to_public(sender, instance, created, **kwargs):
    current_schema = connection.schema_name 

    if current_schema == get_public_schema_name():
        return  

    if not created:
        return 

    try:
        with schema_context('public'):
            tenant = Tenant.objects.get(schema_name=current_schema)
    except Tenant.DoesNotExist:
        return

    with schema_context('public'):
        public_user, user_created = User.objects.get_or_create(
            username=instance.username,
            defaults={
                'email': instance.email,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'is_staff': instance.is_staff,
                'is_superuser': instance.is_superuser,
                'is_active': instance.is_active,
            }
        )
        if instance.password and (user_created or instance.password != public_user.password):
            public_user.set_password(instance.password)

        public_user.tenant = tenant
        public_user.save()