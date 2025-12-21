# jobs/admin.py
from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'sr_no',
        'title',
        'company',
        'user',     
    )
    ordering = ('id',) 

    def sr_no(self, obj):
        return obj.id   # or custom serial logic
    
    sr_no.short_description = "No."