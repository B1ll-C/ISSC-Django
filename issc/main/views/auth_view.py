from django.http import HttpResponse,JsonResponse
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

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.contrib import messages

import pandas as pd
from datetime import datetime


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



# @login_required(login_url='/login/')
def signup(request):
    user = AccountRegistration.objects.filter(username=request.user).values()

    users_list = AccountRegistration.objects.all().order_by('-date_joined')
    # users = paginate(users_list,request)


    template = loader.get_template('signup.html')
    context = {
        'user_role': user[0]['privilege'],
        'user_data':user[0],
        'users':users_list
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

def logout(request):
    auth_logout(request)
    return redirect('login')

def import_data(request):
    template = loader.get_template('import.html')
    context = {}

    if request.method == 'POST':
        import_type = request.POST.get('import_type')
        excel_file = request.FILES.get('excel_file')
        print(import_type)

        if not import_type:
            context['error'] = "Please select an import type."
        elif not excel_file:
            context['error'] = "Please select an Excel file."
        else:
            try:
                df = pd.read_excel(excel_file)

                print(import_type=='user')

                if import_type == "user":
                    print("Reached import_data view")  # Debug
                    for index, row in df.iterrows():
                        try:
                            user = AccountRegistration(
                                username=row['ID Number'],
                                first_name=row['First Name'],
                                middle_name=row['Middle Name'],
                                last_name=row['Last Name'],
                                email=row['email'],
                                id_number=row['ID Number'],
                                contact_number=row['contact number'],
                                gender={'Male': 'M', 'Female': 'F', 'Others': 'O'}.get(row['gender'], 'O'),
                                department=row['department'],
                                privilege=row['priv'],
                                status='allowed',
                            )
                            user.set_password('password')
                            user.save()
                            print(df)

                            print(f"Saved User: {row['First Name']} - {row['ID Number']}")
                        except Exception as inner_e:
                            print(f"Error saving user row {index + 1}: {inner_e}")

                    context['message'] = "User data imported successfully!"

                elif import_type == "vehicle":
                    for index, row in df.iterrows():
                        try:
                            vehicle = VehicleRegistration(
                                first_name=row['First Name'],
                                middle_name=row['Middle Name'],
                                last_name=row['Last Name'],
                                id_number=row['ID Number'],
                                contact_number=row['contact number'],
                                email_address=row['email'],
                                role=row['role'],
                                vehicle_type=row['vehicle_type'],
                                color=row['color'],
                                model=row['model'],
                                plate_number=row['plate_number'],
                                sticker_number=row['sticker_number'],
                                drivers_license=row['drivers_license'],
                                guardian_name=row['guardian_name'],
                                guardian_number=row['guardian_contact'],
                                status='allowed',
                                image=None,
                                qr_code=None,
                                is_archived=False
                            )
                            vehicle.save()

                            print(f"Saved Vehicle: {row['plate_number']}")
                        except Exception as inner_e:
                            print(f"Error saving vehicle row {index + 1}: {inner_e}")

                    context['message'] = "Vehicle data imported successfully!"

                else:
                    context['error'] = "Invalid import type selected."

            except Exception as e:
                context['error'] = f"Error processing Excel file: {str(e)}"
                print(f"Error processing Excel file: {str(e)}")

    return HttpResponse(template.render(context, request))



def getUser(request):
    user_type = request.GET.get('type', '').strip().lower()
    current_year = datetime.now().year

    if user_type not in ['student', 'faculty']:
        return JsonResponse({'error': 'Invalid or missing user type'}, status=400)

    if user_type == 'student':
        prefix = f"{current_year}-"
        latest = (
            AccountRegistration.objects.filter(
                id_number__startswith=prefix,
                privilege__iexact='student'
            )
            .order_by('-id_number')
            .values('id_number')
            .first()
        )

        if latest:
            # Extract and increment the middle part of the ID
            parts = latest['id_number'].split('-')
            try:
                next_id = int(parts[1]) + 1
            except (IndexError, ValueError):
                next_id = 1
        else:
            next_id = 1

        new_id = f"{current_year}-{str(next_id).zfill(5)}-CL-0"
        return JsonResponse({'id_number': new_id})

    else:  # faculty
        latest = (
            AccountRegistration.objects.filter(
                privilege__iexact='faculty'
            )
            .order_by('-id_number')
            .values('id_number')
            .first()
        )

        if latest:
            try:
                next_id = int(latest['id_number']) + 1
            except ValueError:
                next_id = 1
        else:
            next_id = 1

        new_id = str(next_id).zfill(5)
        return JsonResponse({'id_number': new_id})

# def password_reset(request):
#     if request.method == "POST":
#         email = request.POST.get("email")  # Get the email from the form
#         form = PasswordResetForm({"email": email})

#         if form.is_valid():
#             form.save(
#                 request=request,
#                 use_https=request.is_secure(),
#                 email_template_name="registration/password_reset_email.html"
#             )
#             messages.success(request, "A password reset link has been sent to your email.")
#             return redirect("password_reset_done")  # Redirect to a confirmation page

#         else:
#             messages.error(request, "Invalid email address. Please try again.")

#     else:
#         form = PasswordResetForm()

#     return render(request, "test.html")


from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/acc_reset.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'registration/acc_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/acc_reset_done.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/acc_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'registration/acc_reset_complete.html'
