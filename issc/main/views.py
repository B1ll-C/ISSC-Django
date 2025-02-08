from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

user_roles = ['admin','student','faculty']
i = 0

def base(request):
    template = loader.get_template('dashboard/dashboard.html')
    context = {}
    return HttpResponse(template.render(context, request))

    
def index(request):
    user_role = user_roles[i]
    template = loader.get_template('index.html')
    context = {
        'user_role': user_role
    }
    return HttpResponse(template.render(context, request))

def incident(request):
    user_role = user_roles[i]
    template = loader.get_template('incident/incident.html')
    context = {
        'user_role': user_role
    }
    return HttpResponse(template.render(context, request))

def vehicles(request):
    user_role = user_roles[i]
    template = loader.get_template('vehicle/vehicle.html')
    context = {
        'user_role': user_role
    }
    return HttpResponse(template.render(context, request))

def live_feed(request):
    user_role = user_roles[i]
    template = loader.get_template('live-feed/live-feed.html')
    context = {
        'user_role': user_role
    }
    return HttpResponse(template.render(context, request))

def about(request):
    user_role = user_roles[i]
    template = loader.get_template('about/about.html')
    context = {
        'user_role': user_role
    }
    return HttpResponse(template.render(context, request))

def logout(request):
    user_role = user_roles[i]
    template = loader.get_template('logout.html')
    context = {
        'user_role': user_role
    }
    return HttpResponse(template.render(context, request))
