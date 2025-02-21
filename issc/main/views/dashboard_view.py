from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from ..models import AccountRegistration, IncidentReport, VehicleRegistration

import calendar
import pandas as pd
from django.utils.timezone import now
from collections import Counter

def incident_rate():
    current_year = now().year
    reports = IncidentReport.objects.filter(date__year=current_year)

    # Count incidents per month
    incident_counts = Counter(report.date.month for report in reports)

    # Ensure all months are represented
    months = list(range(1, now().month + 5))
    counts = [incident_counts.get(m, 0) for m in months]

    # Calculate percentage increase
    percentage_increase = [0]  # First month has no previous data
    for i in range(1, len(counts)):
        prev = counts[i - 1]
        current = counts[i]
        if prev == 0:  # Prevent division by zero
            percentage = 0 if current == 0 else 100
        else:
            percentage = ((current - prev) / prev) * 100
        percentage_increase.append(round(percentage, 2))

    # Plot the data
    plt.figure(figsize=(10, 5))
    bars = plt.bar(months, counts, color="#6AAE43", alpha=0.7)

    # Annotate each bar with percentage increase
    for bar, percent in zip(bars, percentage_increase):
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # Center text on bar
            bar.get_height() + 1,  # Position above the bar
            f"{percent}%",  # Display percentage
            ha="center", va="bottom", fontsize=10, fontweight="bold", color="black"
        )

    plt.xticks(months, [calendar.month_abbr[m] for m in months])
    plt.xlabel("Month")
    plt.ylabel("Number of Incidents")
    plt.title(f"Incident Reports Growth ({current_year})")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Convert plot to image
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    chart = base64.b64encode(image_png).decode("utf-8")

    return chart


def monthly_incident_graph():
    incidents = IncidentReport.objects.all()
    if not incidents.exists():
        return None
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
    if not incidents.exists():
        return None
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

def vehicle_graph():
    data = VehicleRegistration.objects.values('role', 'vehicle_type')

    if not data.exists():  # Check if the queryset is empty
        return None  # Return None or a placeholder image if needed

    df = pd.DataFrame(list(data))

    if df.empty:  # Additional safeguard if DataFrame is empty
        return None

    counts = df.groupby(['role', 'vehicle_type']).size().unstack(fill_value=0)

    plt.figure(figsize=(10, 5))
    counts.plot(kind='bar')

    plt.title('Type of Owner and Type of Vehicle')
    plt.xlabel('Vehicle Type')
    plt.ylabel('Count')
    plt.legend(title='Role')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    img_data = base64.b64encode(buf.read()).decode('utf-8')

    return img_data  # Returns the base64 string of the image




@login_required(login_url='/login/')
def base(request):
    # Use get_object_or_404 to ensure a valid user is retrieved
    user = get_object_or_404(AccountRegistration, username=request.user.username)

    # If the user is not authenticated, redirect (though it's redundant because of the decorator)
    if not request.user.is_authenticated:
        return redirect('login')

    img_data = monthly_incident_graph()
    department_incident_data = department_incident_graph()
    vehicle_data = vehicle_graph()
    incident_data = incident_rate()

    # Pass the image data along with other context variables
    context = {
        'user_role': user.privilege,  # Direct access without using `values()`
        'user_data': user,
        'monthly_incident_data': img_data,  # Pass the base64 image to the template
        'department_incident_data':department_incident_data,
        'vehicle_data':vehicle_graph,
        'incident_data':incident_data
    }

    # Render the template with the context
    return render(request, 'dashboard/dashboard.html', context)
