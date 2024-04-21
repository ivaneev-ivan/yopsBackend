from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, ServerLocation, ConfigKey
from .permissions import IsAdminOrReadOnly, IsOwner, IsAdmin
from .serializers import OrderSerializer, ServerLocationSerializer, ConfigSerializer
from .auth import CsrfExemptSessionAuthentication
from rest_framework.authentication import TokenAuthentication


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    authentication_classes = (CsrfExemptSessionAuthentication, TokenAuthentication)

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user).all()
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ServerLocationViewSet(viewsets.ModelViewSet):
    queryset = ServerLocation.objects.all()
    serializer_class = ServerLocationSerializer
    permission_classes = [IsAdminOrReadOnly]

@api_view(['GET'])
def get_user_configs_by_id(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.user.id != request.user.id:
        return Response({'message': 'error', 'detail': 'You don\'t have permission'},
                        status=status.HTTP_400_BAD_REQUEST)
    user_configs = ConfigKey.objects.filter(order=order)
    user_configs_serializer = ConfigSerializer(user_configs, many=True)

    return Response( user_configs_serializer.data
    , status=status.HTTP_200_OK)

