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


from ..computer_vision.face_enrollment import FaceEnrollment



@login_required(login_url='/login')
def face_enrollment(request):
    user = AccountRegistration.objects.filter(username=request.user).values()

    if not user.exists():
        return HttpResponse("User not found", status=404)

    user_id_number = user[0]['id_number']
    enroller = FaceEnrollment(source=0)
    result = enroller.enroll_face(user_id_number)

    return render(request, 'face_enrollment/face.html', {'result': result})
    

@login_required(login_url='/login')
def enroll_face(request):
    """Handles face enrollment when capture button is clicked."""
    if request.method == "POST":
        user = AccountRegistration.objects.filter(username=request.user).values()

        if not user.exists():
            return JsonResponse({"status": "error", "message": "User not found."})

        user_id_number = user[0]['id_number']
        enroller = FaceEnrollment(source=0)
        return enroller.enroll_face(user_id_number)

    return JsonResponse({"status": "error", "message": "Invalid request."})

# @login_required(login_url='/login')
# def face_enrollment(request):
#     user = AccountRegistration.objects.filter(username=request.user).values()
#     template = loader.get_template('face_enrollment/face.html')
#     context ={
#         'user_role': user[0]['privilege'],
#         'user_data':user[0]
#     }

#     return HttpResponse(template.render(context,request))


