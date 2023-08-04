from django.contrib import admin
from apps.vending.models import Product, VendingMachineSlot


# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "created_at", "updated_at"]
    ordering = ["-created_at"]

class VendingMachineSlotAdmin(admin.ModelAdmin):
    list_display = ["product", "quantity", "row", "column"]


admin.site.register(Product, ProductAdmin)
admin.site.register(VendingMachineSlot, VendingMachineSlotAdmin)
