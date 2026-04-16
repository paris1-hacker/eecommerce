from . import views
from django.urls import path



urlpatterns = [
    path('', views.home, name='home'),

    path('shop/', views.shop, name='shop'), 

    path('view/<int:pk>/', views.product_detail, name='view'), 


    path('about/', views.about, name='about'), 


    path('contact/', views.contact, name='contact'),

    path('login/', views.loginPage, name='login'),
    path('forgot-password/', views.forgot, name='forgot-password'), 


    path('wishlist/', views.wishlistt, name='wishlist'), 
    path('single/', views.single, name='single'), 


    path('cart/', views.cart, name='cart'),
    path('category/', views.category, name='category'), 


    path('dashboard/', views.dashboard, name='dashboard'),
    path('checkout/', views.checkout, name='checkout'), 

    path('blog/', views.blog, name='blog'), 

    path('update-item/', views.updateItem, name='update-item'),
    # path('update-cart/', views.updatecart, name='update-cart')
    path('remove-item/', views.removeItem, name='remove-item'),
    
    path('get-shipping-fee/', views.get_shipping_fee, name='get_shipping_fee'),
    

]