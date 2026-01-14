# jobs/admin.py
from django.contrib import admin
from .models import Job, UserProfile
from django.utils.html import format_html

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
    list_display = ('user', 'resume_link', 'updated_at')
    search_fields = ('user__username', 'user__email')

    def resume_link(self, obj):
        if obj.resume:
            return format_html("<a href='{}' target='_blank'>Download</a>", obj.resume.url)
        return "-"
    resume_link.short_description = "Resume"

    def resume_preview(self, obj):
        if obj.resume:
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                obj.resume.url,
                obj.resume.name
            )
        return "No resume uploaded"
    resume_preview.short_description = "Current Resume"