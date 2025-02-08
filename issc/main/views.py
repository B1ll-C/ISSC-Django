from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

# Create your views here.
user_roles = ['admin','student','faculty']

def index(request):
    
    user_role = user_roles[1]
    template = loader.get_template('index.html')
    context = {
        'user_role':user_role
    }


    return HttpResponse(template.render(context, request))

def incident(request):
    return render(request, 'incident.html')

def vehicles(request):
    return render(request,'vehicle.html')

def live_feed(request):
    return render(request, 'live-feed.html')

def about(request):
    return render(request, 'about.html')

def logout(request):
    pass
