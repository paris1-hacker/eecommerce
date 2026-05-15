from django.urls import path
from . import views

# route ur views here


urlpatterns = [
    path('login/', views.loginPage, name='login'), 
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutUser, name='logout'),
    path('dashboard/', views.dashboard, name="dashboard"), 
    path('order-detail/<int:pk>', views.orderDetail, name='order-detail'),
]
