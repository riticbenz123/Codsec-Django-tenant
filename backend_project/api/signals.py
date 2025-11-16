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
    """
    When a User is created in a tenant schema (e.g. flat1),
    copy it to public schema and set tenant field.
    """
    current_schema = connection.schema_name  # ← Use this

    if current_schema == get_public_schema_name():
        return  # Don't sync public → public

    if not created:
        return  # Only on create

    # Get tenant from public schema
    try:
        with schema_context('public'):
            tenant = Tenant.objects.get(schema_name=current_schema)
    except Tenant.DoesNotExist:
        return

    # Create or update user in public schema
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

        # Sync password (hashed)
        if instance.password and (user_created or instance.password != public_user.password):
            public_user.set_password(instance.password)

        public_user.tenant = tenant
        public_user.save()