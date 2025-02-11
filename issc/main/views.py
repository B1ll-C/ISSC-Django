from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

from .models import AccountRegistration



    
def login(request):
    template = loader.get_template('login.html')
    context = {}
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # print(email)
        # print(password)
        user = authenticate(request, username=username,password=password)
        if user:
            auth_login(request, user)
            return redirect('dashboard') 

    return HttpResponse(template.render(context,request))



@login_required(login_url='/login/')
def signup(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    template = loader.get_template('signup.html')
    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0]
    }

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        id_number = request.POST.get('id_number')
        contact_number = request.POST.get('contact_number')
        gender = request.POST.get('gender')
        department = request.POST.get('department')
        privilege = request.POST.get('privilege')
        status = request.POST.get('status')
        password = request.POST.get('password')

        print(password)

        user = AccountRegistration(
            username=username,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            id_number=id_number,
            contact_number=contact_number,
            gender=gender,
            department=department,
            privilege=privilege,
            status=status,
            password=password
        )

        user.set_password(password)
        user.save()
        return redirect('signup')
    return HttpResponse(template.render(context,request))


@login_required(login_url='/login/')
def base(request):
    user = AccountRegistration.objects.filter(username=request.user).values()

    if not request.user.is_authenticated:
        redirect('login')
    template = loader.get_template('dashboard/dashboard.html')
    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0]
    }

    return HttpResponse(template.render(context, request))

@login_required(login_url='/login/')
def incident(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    if user[0]['privilege'] == 'student':
        template = loader.get_template('incident/student/incident.html')
    else:
        template = loader.get_template('incident/admin/incident.html')

        
    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0]

    }
    return HttpResponse(template.render(context, request))
@login_required(login_url='/login/')
def incident_forms(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    template = loader.get_template('incident/forms.html')
    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0]

    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login/')
def vehicles(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    if user[0]['privilege'] == 'student' :
        template = loader.get_template('vehicle/student/vehicle.html')
    else:
        template = loader.get_template('vehicle/admin/vehicle.html')

    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0]

    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login/')
def vehicle_forms(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    template = loader.get_template('vehicle/forms.html')

    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0]

    }
    return HttpResponse(template.render(context,request))


@login_required(login_url='/login/')
def live_feed(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    template = loader.get_template('live-feed/live-feed.html')
    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0]

    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login/')
def about(request):
    user = AccountRegistration.objects.filter(username=request.user).values()

    template = loader.get_template('about/about.html')
    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0]

    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login')
def face_enrollment(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    template = loader.get_template('face_enrollment/face.html')
    context ={
        'user_role': user[0]['privilege'],
        'user_data':user[0]
    }

    return HttpResponse(template.render(context,request))

def logout(request):
    auth_logout(request)
    return redirect('login')
