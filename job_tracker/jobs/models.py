from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
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
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    job = models.ForeignKey("Job", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"
