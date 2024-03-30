from rest_framework import permissions, viewsets
from .models import Order, ServerLocation
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly, IsOwner, IsAdmin
from .serializers import OrderSerializer, ServerLocationSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner, IsAdmin]

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user).all()
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ServerLocationViewSet(viewsets.ModelViewSet):
    queryset = ServerLocation.objects.all()
    serializer_class = ServerLocationSerializer
    permission_classes = [IsAdminOrReadOnly]
