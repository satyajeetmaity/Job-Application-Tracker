from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import os
# Create your models here.
class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('interview', 'Interview'),
        ('offered', 'Offered'),
        ('rejected', 'Rejected'),
    ]
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    apply_date = models.DateField()
    notes = models.TextField(blank=True)
    priority = models.CharField(max_length=10,choices=PRIORITY_CHOICES,default='medium')
    rejection_reason = models.TextField(blank=True)
    follow_up_date = models.DateField(blank=True, null=True)
    contact_name = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    job_url = models.URLField(blank=True)
    source = models.CharField(max_length=50,blank=True, choices=[('linkedin','Linkedin'),('naukri','Naukri'),('company','Company Website'),('referral','Referral'),('other','Other'),])
    next_step = models.CharField(max_length=255, blank=True)
    salary_min = models.IntegerField(blank=True, null=True)
    salary_max = models.IntegerField(blank=True,null=True)
    follow_up_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.company}"
    
    def save(self, *args, **kwargs):
        if self.follow_up_done:
            self.follow_up_date = None
        super().save(*args, **kwargs)

class AdminActivity(models.Model):
    ACTION_CHOICES = [
        ("login", "User Logged In"),
        ("job_created", "Job Created"),
        ("job_updated", "Job Updated"),
        ("followup_done", "Follow-up Done"),
        ("user_locked", "User Locked"),
        ("user_unlocked", "User Unlocked"),
        ("resume_uploaded", "Resume Uploaded"),
        ("resume_updated", "Resume Updated"),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    job = models.ForeignKey("Job", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"

def resume_upload_path(instance, filename):
    #media/resumes/user_<id>/<filename>
    return f"resumes/user_{instance.user.id}/{filename}"

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    resume = models.FileField(upload_to=resume_upload_path, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old = UserProfile.objects.get(pk=self.pk)
                if old.resume and old.resume != self.resume:
                    if old.resume and old.resume.path and os.path.isfile(old.resume.path):
                        os.remove(old.resume.path)
            except UserProfile.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
    
class ResumeBuilder(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    summary = models.TextField(blank=True)
    skills = models.TextField(help_text="Comma Separated Skills", blank=True)
    experience = models.TextField(blank=True)
    projects = models.TextField(blank=True)
    education = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Resume"