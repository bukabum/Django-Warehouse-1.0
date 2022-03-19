from django.contrib import admin
from .models import * 
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.
#class SparePartAdmin(admin.ModelAdmin):
#    readonly_fields = ['name', 'product_code', 'description', 'stock', 'price', 'image', 'qrcode', 'date_added', 'update_date', 'category']
class StockInAdmin(admin.ModelAdmin):
    readonly_fields = ['person_responsible', 'stockin', 'description', 'date_added', 'parts']
class StockOutAdmin(admin.ModelAdmin):
    readonly_fields = ['person_responsible', 'stockout', 'description', 'date_added', 'parts']
class SparePartAdmin(SimpleHistoryAdmin):
    list_display = ['id', 'name']
    history_list_display = ['name']
    search_fields = ['name']
    readonly_fields = ['name', 'price', 'product_code', 'person_responsible', 'person_responsible_for_update', 'qrcode', 'description', 'stock', 'date_added', 'update_date', 'category', 'first_stock']
class EnhanceInOutStockAdmin(admin.ModelAdmin):
    readonly_fields = ['stockout', 'person_responsible', 'stockin', 'description', 'date_added', 'parts']
class PromotionAdmin(admin.ModelAdmin):
    readonly_fields = ['created_datetime']


admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(Logo)
admin.site.register(SparePart, SparePartAdmin)
admin.site.register(StockIn, StockInAdmin)
admin.site.register(StockOut, StockOutAdmin)
admin.site.register(EnhanceInOutStock, EnhanceInOutStockAdmin)
