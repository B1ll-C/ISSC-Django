from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required


user_roles = ['admin','student','faculty']
i = 0


def login(request):
    template = loader.get_template('login.html')
    context = {}
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(email)
        print(password)
        user = authenticate(request, username=email,password=password)
        if user:
            auth_login(request, user)
            return redirect('dashboard') 

    return HttpResponse(template.render(context,request))

@login_required(login_url='/login/')
def signup(request):
    template = loader.get_template('signup.html')
    context = {}
    return HttpResponse(template.render(context,request))

@login_required(login_url='/login/')
def base(request):
    if not request.user.is_authenticated:
        redirect('login')
    template = loader.get_template('dashboard/dashboard.html')
    context = {}
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login/')
def incident(request):
    user_role = user_roles[i]
    template = loader.get_template('incident/incident.html')
    context = {
        'user_role': user_role
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login/')
def vehicles(request):
    user_role = user_roles[i]
    template = loader.get_template('vehicle/vehicle.html')
    context = {
        'user_role': user_role
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login/')
def live_feed(request):
    user_role = user_roles[i]
    template = loader.get_template('live-feed/live-feed.html')
    context = {
        'user_role': user_role
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login/')
def about(request):
    user_role = user_roles[i]
    template = loader.get_template('about/about.html')
    context = {
        'user_role': user_role
    }
    return HttpResponse(template.render(context, request))

def logout(request):
    auth_logout(request)
    return redirect('login')
