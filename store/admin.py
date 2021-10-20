from django.contrib import admin
from .models import Product,Variations

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display=('product_name','stock','modified_date','price','is_available','category')
    prepopulated_fields={'slug':('product_name',)}

class VariationAdmin(admin.ModelAdmin):
    list_display=('product','is_active','variation_value')
    list_editable=('is_active',)
    list_filter=('product','is_active','variation_value')
    

admin.site.register(Product,ProductAdmin)
admin.site.register(Variations,VariationAdmin)