from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

# Create your views here.



def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponse('come')
        else:
            messages.error(request, 'Invalid Username and Password')


    context = {}
    return render(request, 'login.html', context)