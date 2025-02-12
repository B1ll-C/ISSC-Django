from django.contrib import admin
from .models import AccountRegistration, VehicleRegistration, IncidentReport, FacesEmbeddings
# Register your models here.
admin.site.register(AccountRegistration)
admin.site.register(VehicleRegistration)
admin.site.register(IncidentReport)
admin.site.register(FacesEmbeddings)
