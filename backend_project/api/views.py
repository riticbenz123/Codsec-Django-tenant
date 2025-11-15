from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import render
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, RegisterSerializer

User = get_user_model()


# Create your views here.
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # token = Token.objects.create(user=user)
        refresh = RefreshToken.for_user(user)
        return Response({
            # 'token': token.key,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        # token, _ = Token.objects.get_or_create(user=user)
        refresh = RefreshToken.for_user(user)
        # return Response({'token': token.key})
        user_serializer = LoginSerializer(user)
        return Response({
             'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_serializer.data
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=401)

    groups = list(request.user.groups.values_list('name', flat=True))
    user_permissions = list(request.user.user_permissions.values_list('codename', flat=True))
    group_permissions = []
    for group in request.user.groups.all():
        group_permissions.extend(group.permissions.values_list('codename', flat=True))
    all_permissions = list(set(user_permissions + group_permissions))

    return Response({
        'user': request.user.username,
        'groups': groups,
        'permissions': all_permissions
    })
    
    
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'register': reverse('register', request=request, format=format),
        'login': reverse('login', request=request, format=format),
        'my-permissions': reverse('my-permissions', request=request, format=format),
        'token-refresh': reverse('token_refresh', request=request, format=format),
    })