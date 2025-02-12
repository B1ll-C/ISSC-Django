from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator

from .models import AccountRegistration, IncidentReport, VehicleRegistration





    
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

    users_list = AccountRegistration.objects.all().order_by('-date_joined')
    users = paginate(users_list,request)


    template = loader.get_template('signup.html')
    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0],
        'users':users
    }

    if request.method == 'POST':
        username = request.POST.get('username')
        if 'delete' in request.POST:
            # Handle delete action
            user = AccountRegistration.objects.get(username=username)
            user.delete()
            return redirect('signup')  # Redirect to the same page after deleting

        if 'update' in request.POST:
            # Handle update action (you can collect and update data as needed)
            user = AccountRegistration.objects.get(username=username)
            user.first_name = request.POST.get('first_name')
            user.middle_name = request.POST.get('middle_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.id_number = request.POST.get('id_number')
            user.contact_number = request.POST.get('contact_number')
            user.gender = request.POST.get('gender')
            user.department = request.POST.get('department')
            user.privilege = request.POST.get('privilege')
            user.status = request.POST.get('status')
            user.save()
            print('')
            return redirect('signup')  # Redirect to the same page after updating
    return HttpResponse(template.render(context,request))

def signup_forms(request):
    template = loader.get_template('signup_form.html')
    user = AccountRegistration.objects.filter(username=request.user).values()
    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0],
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
        return redirect('signup-forms')
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
        open_incident = IncidentReport.objects.filter(status='open', id_number=user[0]['id_number']).order_by('date_joined')
        pending_incident = IncidentReport.objects.filter(status='pending', id_number=user[0]['id_number']).order_by('date_joined')
        closed_incident = IncidentReport.objects.filter(status='closed', id_number=user[0]['id_number']).order_by('date_joined')
    else:
        template = loader.get_template('incident/admin/incident.html')
        open_incident = IncidentReport.objects.filter(status='open').order_by('date_joined')
        pending_incident = IncidentReport.objects.filter(status='pending').order_by('date_joined')
        closed_incident = IncidentReport.objects.filter(status='closed').order_by('date_joined')

    open_incident = paginate(open_incident,request)
    pending_incident = paginate(pending_incident,request)
    closed_incident = paginate(closed_incident,request)

    if request.method == 'POST':
        incident_id = request.POST['incident_id']
        status = request.POST['status']

       
        if 'delete' in request.POST:
            incident = IncidentReport.objects.get(id=incident_id)
            incident.delete()
            return redirect('incidents')
            
        if 'update' in request.POST:
            incident = IncidentReport.objects.get(id=incident_id)
            incident.status = status
            incident.save()
            return redirect('incidents')




        
    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0],
        'open_incident':open_incident,
        'pending_incident':pending_incident,
        'closed_incident':closed_incident

    }
    return HttpResponse(template.render(context, request))
@login_required(login_url='/login/')
def incident_details(request, id):
    user = AccountRegistration.objects.filter(username=request.user).values()
    incident = get_object_or_404(IncidentReport, id=id)
    template = loader.get_template('incident/details.html')
    context = {
        'incident':incident,
        'user_role': user[0]['privilege'],
        'user_data':user[0],

    }

    if request.method == 'POST':
        incident_id = request.POST['incident_id']
        status = request.POST['status']

        incident.status = status
        incident.save()



        return redirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponse(template.render(context,request))

@login_required(login_url='/login/')
def incident_forms(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    template = loader.get_template('incident/forms.html')
    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0]

    }

    if request.method == 'POST':
        first_name = request.POST['first_name']
        middle_name = request.POST.get('middle_name', '')  # Optional field
        last_name = request.POST['last_name']
        contact_number = request.POST['contact_number']
        id_number = request.POST['id_number']
        subject = request.POST['subject']
        location = request.POST['location']
        incident = request.POST['incident']
        request_for_action = request.POST['request_for_action']
        reported_by = request.POST['reported_by']
        position = request.POST['position']
        department = request.POST['department']
        phone_number = request.POST['phone_number']
        status = request.POST['status']
        file = request.FILES.get('file', None)

        # Create and save the incident report manually
        report = IncidentReport(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            contact_number=contact_number,
            id_number=id_number,
            subject=subject,
            location=location,
            incident=incident,
            request_for_action=request_for_action,
            reported_by=reported_by,
            position=position,
            department=department,
            phone_number=phone_number,
            status=status,
            file=file
        )
        report.save()
        
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login/')
def vehicles(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    if user[0]['privilege'] == 'student' :
        template = loader.get_template('vehicle/student/vehicle.html')
        allowed_vehicle_type = VehicleRegistration.objects.filter(status='allowed').order_by('date_joined')
        restricted_vehicle_type = VehicleRegistration.objects.filter(status='restricted').order_by('date_joined')
    else:
        template = loader.get_template('vehicle/admin/vehicle.html')
        allowed_vehicle_type = VehicleRegistration.objects.filter(status='allowed').order_by('date_joined')
        restricted_vehicle_type = VehicleRegistration.objects.filter(status='restricted').order_by('date_joined')

    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0],
        'allowed_vehicles':allowed_vehicle_type,
        'restricted_vehicles':restricted_vehicle_type,

    }

    if request.method == 'POST':
        vehicle_id = request.POST['vehicle_id']
        status = request.POST['status']
        if 'delete' in request.POST:
            vehicle = VehicleRegistration.objects.get(id=vehicle_id)
            vehicle.delete()
        if 'update' in request.POST:
            vehicle = VehicleRegistration.objects.get(id=vehicle_id)
            vehicle.status = status
            vehicle.save()


    return HttpResponse(template.render(context, request))
@login_required(login_url='/login/')
def vehicle_details(request, id):
    user = AccountRegistration.objects.filter(username=request.user).values()
    vehicle = get_object_or_404(VehicleRegistration, id=id)
    template = loader.get_template('vehicle/details.html')
    context = {
        'vehicle':vehicle,
        'user_role': user[0]['privilege'],
        'user_data':user[0],

    }

    if request.method == 'POST':
        status = request.POST['status']

        vehicle.status = status
        vehicle.save()



        return redirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponse(template.render(context,request))
@login_required(login_url='/login/')
def vehicle_forms(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    template = loader.get_template('vehicle/forms.html')

    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0]

    }

    if request.method == 'POST':
        first_name = request.POST['first_name']
        middle_name = request.POST.get('middle_name', '')  # Optional field
        last_name = request.POST['last_name']
        id_number = request.POST['id_number']
        contact_number = request.POST['contact_number']
        email_address = request.POST['email_address']
        role = request.POST['role']
        vehicle_type = request.POST['vehicle_type']
        color = request.POST['color']
        model = request.POST['model']
        plate_number = request.POST['plate_number']
        sticker_number = request.POST['sticker_number']
        drivers_license = request.POST['drivers_license']
        guardian_name = request.POST['guardian_name']
        guardian_number = request.POST['guardian_number']
        status = request.POST['status']
        image = request.FILES.get('image')
        qr_code = request.FILES.get('qr_code')

        # Create a new VehicleRegistration instance and save it to the database
        vehicle = VehicleRegistration(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            id_number=id_number,
            contact_number=contact_number,
            email_address=email_address,
            role=role,
            vehicle_type=vehicle_type,
            color=color,
            model=model,
            plate_number=plate_number,
            sticker_number=sticker_number,
            drivers_license=drivers_license,
            guardian_name=guardian_name,
            guardian_number=guardian_number,
            status=status,
            image=image,
            qr_code=qr_code
        )
        vehicle.save()
        

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


def image_test(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    print(user[0]['id_number'])
    template = loader.get_template('test.html')
    reports = VehicleRegistration.objects.all()
    context = {
        'reports':reports
    }
    return HttpResponse(template.render(context,request))


def paginate(queryset, request, per_page=5):
        paginator = Paginator(queryset, per_page)
        page = request.GET.get('page')
        return paginator.get_page(page)