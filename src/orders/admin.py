from django.contrib import admin
from .models import ServerLocation, Order


@admin.register(ServerLocation)
class ServerLocationModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'solar')


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'count_configs', 'is_own_server', 'user', 'location', 'solar')
    readonly_fields = ('id', 'solar')
