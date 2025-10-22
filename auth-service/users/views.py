from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User

@api_view(['POST'])
def register(request):
    email = request.data.get('email')
    password = request.data.get('password')
    if not email or not password:
        return Response({'error': 'Email y password son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Usuario ya existe'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(email=email, password=password)
    return Response({'message': 'Usuario creado exitosamente'})

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response({
        'id': user.id,
        'email': user.email,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
    })
