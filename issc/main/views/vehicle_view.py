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

from django.template.loader import render_to_string
import pdfkit

@login_required(login_url='/login/')
def vehicles(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    is_archived = request.GET.get('archive', 'false').lower() == 'true'

    if user[0]['privilege'] == 'student' :
        template = loader.get_template('vehicle/student/vehicle.html')
        # Removed the filtering for restricted vehicles
        registered_vehicle = VehicleRegistration.objects.filter(is_archived=is_archived, id_number=user[0]['id_number']).order_by('id_number')
    else:
        template = loader.get_template('vehicle/admin/vehicle.html')
        # Removed the filtering for restricted vehicles
        registered_vehicle = VehicleRegistration.objects.filter(is_archived=is_archived).order_by('id_number')

    context = {
        'user_role': user[0]['privilege'],
        'user_data': user[0],
        'registered_vehicle': registered_vehicle,  # still using this name but now includes all vehicles
        'is_archived': is_archived
    }

    if request.method == 'POST':
        vehicle_id = request.POST['vehicle_id']
        vehicle = VehicleRegistration.objects.get(id=vehicle_id)
        status = request.POST['status']
        if 'delete' in request.POST:
            vehicle.is_archived = True
            vehicle.last_updated_by = user[0]['id_number']
            vehicle.save()
        if 'update' in request.POST:
            vehicle.status = status
            vehicle.last_updated_by = user[0]['id_number']
            vehicle.save()

        if 'restore' in request.POST:
            vehicle.is_archived = False
            vehicle.last_updated_by = user[0]['id_number']
            vehicle.save()

    return HttpResponse(template.render(context, request))
@login_required(login_url='/login/')
def vehicle_print(request, id):
    # Get user data
    user = AccountRegistration.objects.filter(username=request.user).values()
    
    # Get vehicle data
    vehicle = get_object_or_404(VehicleRegistration, id=id)
    
    # Prepare the context for rendering the template
    context = {
        'vehicle': vehicle,
        'user_role': user[0]['privilege'],
        'user_data': user[0],
    }

    # Render the template to a string
    html_string = render_to_string('vehicle/print.html', context)
    
    # Configure pdfkit to use wkhtmltopdf (make sure it's in your system path)
    # You can also pass additional options to pdfkit as needed (e.g., for page size, margins, etc.)
    pdf_file = pdfkit.from_string(html_string, False)
    
    # Return the generated PDF as a downloadable file
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="vehicle_{id}_report.pdf"'
    
    return response

@login_required(login_url='/login/')
def vehicle_details(request, id):
    user = AccountRegistration.objects.filter(username=request.user).values()
    vehicle = get_object_or_404(VehicleRegistration, id=id)
    template = loader.get_template('vehicle/details.html')
    context = {
        'vehicle': vehicle,
        'user_role': user[0]['privilege'],
        'user_data': user[0],
    }

    if request.method == 'POST':
        status = request.POST['status']
        vehicle.last_updated_by = user[0]['id_number']
        vehicle.status = status
        vehicle.save()

        return redirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponse(template.render(context, request))

@login_required(login_url='/login/')
def vehicle_forms(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    template = loader.get_template('vehicle/forms.html')

    context = {
        'user_role': user[0]['privilege'],
        'user_data': user[0]
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
        status = 'restricted' if user[0]['privilege'] == 'student' else request.POST['status']
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
            qr_code=qr_code,
            is_archived=False
        )
        vehicle.save()

    return HttpResponse(template.render(context, request))
