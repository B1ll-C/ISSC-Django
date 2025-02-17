from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from ..models import AccountRegistration, IncidentReport, VehicleRegistration

import calendar

from collections import Counter
def monthly_incident_graph():
    incidents = IncidentReport.objects.all()
    months = [incident.date.strftime('%B') for incident in incidents]

    month_counts = Counter(months)
    all_months = list(calendar.month_name)[1:]
    incident_data = [month_counts.get(month, 0) for month in all_months]

    plt.figure(figsize=(10, 5))
    plt.bar(all_months, incident_data, color='skyblue')
    plt.xlabel("Month")
    plt.ylabel("Number of Incidents")
    plt.title("Monthly Incident Report")
    plt.xticks(rotation=45)

    buf = BytesIO()

    plt.savefig(buf, format='png')
    buf.seek(0)


    img_data = base64.b64encode(buf.read()).decode('utf-8')

    return img_data





def department_incident_graph():
    incidents = IncidentReport.objects.all()
    departments = [incident.department for incident in incidents]

    # Count incidents per department
    department_counts = Counter(departments)
    department_names = list(department_counts.keys())
    incident_data = list(department_counts.values())

    # Create plot
    plt.figure(figsize=(10, 5))
    plt.bar(department_names, incident_data, color='lightcoral')
    plt.xlabel("Department")
    plt.ylabel("Number of Incidents")
    plt.title("Incidents by Department")
    plt.xticks(rotation=45)

    buf = BytesIO()

    plt.savefig(buf, format='png')
    buf.seek(0)


    img_data = base64.b64encode(buf.read()).decode('utf-8')

    return img_data




@login_required(login_url='/login/')
def base(request):
    # Use get_object_or_404 to ensure a valid user is retrieved
    user = get_object_or_404(AccountRegistration, username=request.user.username)

    # If the user is not authenticated, redirect (though it's redundant because of the decorator)
    if not request.user.is_authenticated:
        return redirect('login')

    img_data = monthly_incident_graph()
    department_incident_data = department_incident_graph()

    # Pass the image data along with other context variables
    context = {
        'user_role': user.privilege,  # Direct access without using `values()`
        'user_data': user,
        'monthly_incident_data': img_data,  # Pass the base64 image to the template
        'department_incident_data':department_incident_data
    }

    # Render the template with the context
    return render(request, 'dashboard/dashboard.html', context)
