from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator

from ..models import AccountRegistration, IncidentReport, VehicleRegistration

from .utils import paginate

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

