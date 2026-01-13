# jobs/admin.py
from django.contrib import admin
from .models import Job, UserProfile

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

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'resume')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('resume',)
