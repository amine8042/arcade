from django.contrib import admin
from .models import User, MachineArcade, Panne, Maintenance

admin.site.register(User)
admin.site.register(MachineArcade)
admin.site.register(Panne)
admin.site.register(Maintenance)
