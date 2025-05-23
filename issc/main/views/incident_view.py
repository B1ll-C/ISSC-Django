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
def incident(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    is_archived = request.GET.get('archive', 'false').lower() == 'true'
    if user[0]['privilege'] == 'student':
        template = loader.get_template('incident/student/incident.html')
        open_incident = IncidentReport.objects.filter(status='open', id_number=user[0]['id_number'] , is_archived=is_archived).order_by('date_joined')
        pending_incident = IncidentReport.objects.filter(status='pending', id_number=user[0]['id_number'] , is_archived=is_archived).order_by('date_joined')
        closed_incident = IncidentReport.objects.filter(status='closed', id_number=user[0]['id_number'] , is_archived=is_archived).order_by('date_joined')
    else:
        template = loader.get_template('incident/admin/incident.html')
        open_incident = IncidentReport.objects.filter(status='open', is_archived=is_archived).order_by('date_joined')
        pending_incident = IncidentReport.objects.filter(status='pending', is_archived=is_archived).order_by('date_joined')
        closed_incident = IncidentReport.objects.filter(status='closed', is_archived=is_archived).order_by('date_joined')


    if request.method == 'POST':
        incident_id = request.POST['incident_id']
        incident = IncidentReport.objects.get(id=incident_id)

       
        if 'delete' in request.POST:
            incident.is_archived = True
            incident.last_updated_by = user[0]['id_number']
            incident.save()
            return redirect('incidents')
            
        if 'update' in request.POST:
            status = request.POST['status']
            incident.status = status
            incident.last_updated_by = user[0]['id_number']
            incident.save()
            return redirect('incidents')

        if 'restore' in request.POST:
            incident.is_archived = False
            incident.last_updated_by = user[0]['id_number']
            incident.save()
            return redirect('incidents')

    context = {
        'user_role': user[0]['privilege'],
        'user_data': user[0],
        'open_incident': open_incident,
        'pending_incident': pending_incident,
        'closed_incident': closed_incident,
        'is_archived': is_archived
    }

    return HttpResponse(template.render(context, request))

@login_required(login_url='/login/')
def incident_details(request, id):
    user = AccountRegistration.objects.filter(username=request.user).values()
    incident = get_object_or_404(IncidentReport, id=id)
    template = loader.get_template('incident/details.html')
    context = {
        'incident': incident,
        'user_role': user[0]['privilege'],
        'user_data': user[0],
    }

    if request.method == 'POST':
        status = request.POST['status']
        incident.last_updated_by = user[0]['id_number']
        incident.status = status
        incident.save()

        return redirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponse(template.render(context, request))

@login_required(login_url='/login/')
def incident_print(request, id):
    user = AccountRegistration.objects.filter(username=request.user).values()
    incident = get_object_or_404(IncidentReport, id=id)
    template = loader.get_template('incident/print.html')
    context = {
        'incident': incident,
        'user_role': user[0]['privilege'],
        'user_data': user[0],
    }

    if request.method == 'POST':
        status = request.POST['status']
        incident.last_updated_by = user[0]['id_number']
        incident.status = status
        incident.save()

        return redirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponse(template.render(context, request))
@login_required(login_url='/login/')
def incident_forms(request):
    user = AccountRegistration.objects.filter(username=request.user).values()
    template = loader.get_template('incident/forms.html')

    context = {
        'user_role': user[0]['privilege'],
        'user_data': user[0]
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
        status = 'pending' if user[0]['privilege'] == 'student' else request.POST['status']
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
            file=file,
            is_archived=False
        )
        report.save()

    return HttpResponse(template.render(context, request))
