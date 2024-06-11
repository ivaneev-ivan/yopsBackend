from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter
from orders.views import OrderViewSet, ServerLocationViewSet, get_user_configs_by_id, get_server_ip

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'locations', ServerLocationViewSet, basename='locations')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('api/', include(router.urls)),
    path('api/user-configs/<int:pk>/', get_user_configs_by_id, name="user-configs-detail"),
    path('api/orders/ip/<int:pk>/', get_server_ip, name="get-server-ip"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
