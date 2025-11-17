from django.contrib.auth import get_user_model
from django.http import Http404
from django_tenants.utils import get_public_schema_name, get_tenant_model

User = get_user_model()
Tenant = get_tenant_model()
from rest_framework.exceptions import NotAuthenticated

# class TenantScopeMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)

#         if not hasattr(request, 'tenant'):
#             return response

#         if request.tenant.schema_name == get_public_schema_name():
#             return response

#         if not request.user.is_authenticated:
#             raise Http404("Tenant requires authentication")

#         if request.user.is_superuser:
#             return response

#         if request.user.tenant != request.tenant:
#             raise Http404("You do not have access to this flat")

#         return response




PUBLIC_TENANT_PATHS = [
    '/admin/',
    '/admin/login/',
    '/admin/logout/',
    '/admin/password_change/',
    '/admin/password_change/done/',
    '/api/login/',
    '/api/register/',
]

STATIC_MEDIA_PATHS = ['/static/', '/media/']


class TenantScopeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if not hasattr(request, 'tenant'):
            return response

        tenant = request.tenant

        if tenant.schema_name == get_public_schema_name():
            return response

        path = request.path

        if request.method == 'OPTIONS':
            return response
        if any(path.startswith(p) for p in STATIC_MEDIA_PATHS):
            return response
        if any(path.startswith(p) for p in PUBLIC_TENANT_PATHS):
            return response

        print(request.user)
        if not request.user.is_authenticated:
            raise NotAuthenticated("Authentication required for this tenant.")

        if request.user.is_superuser:
            return response
        print(request.user)
        print(getattr(request.user, 'tenant', None))
        print(tenant)
        

        if getattr(request.user, 'tenant', None) != tenant:
            print("NO access")
            raise Http404("You do not have access to this tenant.")

        return response