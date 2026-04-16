from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(Product)

admin.site.register(Customer)

admin.site.register(Variation)

admin.site.register(Order)
admin.site.register(OrderItem)

admin.site.register(Cart)
admin.site.register(CartItem)

admin.site.register(Review)


admin.site.register(SubCategory)
admin.site.register(Category)



admin.site.register(ShippingFee)

admin.site.register(ShippingAddress)