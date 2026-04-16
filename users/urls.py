from django.urls import path
from . import views

# route ur views here


urlpatterns = [
    path('login', views.loginPage, name='login')
]
