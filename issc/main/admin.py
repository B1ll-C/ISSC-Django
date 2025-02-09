from django.contrib import admin
from .models import AccountRegistration, VehicleRegistration, IncidentReport
# Register your models here.
admin.site.register(AccountRegistration)
admin.site.register(VehicleRegistration)
admin.site.register(IncidentReport)
