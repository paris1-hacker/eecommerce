from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from commerce.models import *


# Create your views here.



def loginPage(request):
   
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')


        user = authenticate(request, username=username, password=password)

        print('USER', user)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse('Invalid username or password')
            # messages.error(request, 'Invalid Username and Password')


    context = {}
    return render(request, 'login.html', context)

def registerPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return HttpResponse('Passwords do not match')
            # messages.error(request, 'Passwords do not match')
        
        if User.objects.filter(username=username).exists():
            return HttpResponse('Username already exists')
            # messages.error(request, 'Username already exists')

        if User.objects.filter(email=email).exists():
            return HttpResponse('Email already exists')
            # messages.error(request, 'Email already exists')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        return redirect('home')
    context = {}
    return render(request, 'register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home') 


def dashboard(request):
    customer = request.user.customer
    orders = customer.order_set.all()
    
    # count = []
    # for order in orders:
    #    count.append( order.created_at)
    # print('.............',count)

    context = {'orders':orders,}
    return render(request, 'dashboard.html', context)



def orderDetail(request, pk):
    order = Order.objects.get(id=pk)
    items = order.orderitem_set.all()
    subtotal = order.subtotal 
    print('.......', items)


    return render(request, 'order-detail.html', {'items':items, 'subtotal':subtotal}) 