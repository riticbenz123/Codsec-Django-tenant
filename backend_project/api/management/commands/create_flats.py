import os
from django.core.management.base import BaseCommand
from api.models import Tenant, Domain

class Command(BaseCommand):
    def handle(self, *args, **options):
        os.makedirs('api/management/commands', exist_ok=True)
        flats = ['Flat 1', 'Flat 2', 'Flat 3']
        for i, name in enumerate(flats, 1):
            schema = f'flat{i}'
            domain = f'{schema}.localhost'

            tenant, created = Tenant.objects.get_or_create(
                schema_name=schema,
                defaults={'name': name, 'paid_until': '2026-12-31'}
            )
            if created:
                Domain.objects.create(domain=domain, tenant=tenant, is_primary=True)
                print(f"Created: {name} → http://{domain}:8000")