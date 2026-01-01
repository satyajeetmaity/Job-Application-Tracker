from urllib import request
from django.core.paginator import Paginator
import csv
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils import timezone
import datetime
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from .models import Job
from django.db.models import Q, Case, When, Value, IntegerField, CharField
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import JobForm, CustomUserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .tokens import email_verification_token

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        jobs = Job.objects.filter(user=request.user)
        total_all = jobs.count()
        total_applied = jobs.filter(status='applied').count()
        total_interview = jobs.filter(status='interview').count()
        total_offered = jobs.filter(status='offered').count()
    else:
        total_all = 0
        total_applied = 0
        total_interview = 0
        total_offered = 0
    return render(request, 'jobs/home.html',{'total_all':total_all,'total_applied':total_applied, 'total_interview':total_interview, 'total_offered':total_offered})


def signup(request):
    if request.user.is_authenticated:
        return redirect('job_list')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) #don't save yet
            user.is_active = True  # Set to False if email verification is implemented 
            user.save()

            token = email_verification_token.make_token(user)
            link = request.build_absolute_uri(reverse('verify_email', kwargs={'user_id': user.pk, 'token': token}))
            send_mail("Verify your email",f"Click to verify your account:\n{link}",settings.DEFAULT_FROM_EMAIL,[user.email])
            return render(request, "registration/verify_sent.html", {"email": user.email})
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def verify_email(request, user_id, token):
    user = get_object_or_404(User, pk=user_id)
    if email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('job_list')
    # return render(request, "registration/verify_invalid.html")
    return HttpResponse("Invalid or expired link", status=400)

@login_required
def job_list(request):
    status = request.GET.get('status') #read?status=...
    q = request.GET.get('q')
    date_range = request.GET.get('date') # 'today' or 'week'
    sort = request.GET.get('sort')
    follow = request.GET.get('follow')

    jobs = Job.objects.filter(user=request.user)

    #stats before filtering for display
    total_all = jobs.count()
    total_applied = jobs.filter(status='applied').count()
    total_interview = jobs.filter(status='interview').count()
    total_rejected = jobs.filter(status='rejected').count()
    total_offered = jobs.filter(status='offered').count()
    
    if status in ['applied','interview','rejected','offered']:
        jobs = jobs.filter(status=status)
    if q:
        jobs = jobs.filter(Q(title__icontains=q) | Q(company__icontains=q))

    #always set today once
    today = timezone.localdate()

    if date_range == 'today':
        today = timezone.localdate()
        jobs = jobs.filter(apply_date=today)
    elif date_range == 'week':
        today = timezone.localdate()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        jobs = jobs.filter(apply_date__range=[start_week, end_week])

    if follow == 'today':
        jobs = jobs.filter(follow_up_date=today,follow_up_done=False)
    elif follow == 'overdue':
        jobs = jobs.filter(follow_up_date__lt=today,follow_up_done=False)
    elif follow == 'week':
        start = today
        end = today + timedelta(days=6)
        jobs = jobs.filter(follow_up_date__range=(start, end),follow_up_done=False)

    if sort == 'date':
        jobs = jobs.order_by('apply_date')   #older first
    elif sort == 'date_desc':
        jobs = jobs.order_by('-apply_date') #newest first
    elif sort == 'priority':
        priority_order = Case(
            When(priority='high', then=1),
            When(priority='medium', then=2),
            When(priority='low', then=3),
            output_field=IntegerField(),
        )
        jobs = jobs.order_by(priority_order, 'apply_date')
    else:
        jobs = jobs.order_by('id') #default

    #pagination
    paginator = Paginator(jobs,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for job in page_obj.object_list:
        if job.follow_up_done:
            job.followup_state = "done"
        elif job.follow_up_date:
            if job.follow_up_date < today:
                job.followup_state = "overdue"
            elif job.follow_up_date == today:
                job.followup_state = "today"
            else:
                job.followup_state = "future"
        else:
            job.followup_state = "none"


    return render(request, 'jobs/job_list.html', {'jobs': page_obj.object_list,'page_obj': page_obj, 'current_status':status, 'current_q':q, 'current_date_range':date_range,'current_sort':sort,'current_follow': follow, 'total_all':total_all,
     'total_applied':total_applied, 'total_interview':total_interview, 'total_rejected':total_rejected, 'total_offered':total_offered, 'today': today,})

@login_required
def followup_list(request):
    today = timezone.localdate()
    jobs = Job.objects.filter(user=request.user,follow_up_date__lte=today,follow_up_done=False).exclude(status__in=["rejected", "offered"])
    return render(request, 'jobs/followup_list.html',{'jobs':jobs,'today':today,})

@login_required
def upcoming_followups(request):
    today = timezone.localdate()
    week_later = today + timedelta(days=6)
    jobs = Job.objects.filter(user=request.user,follow_up_date__gte=today,follow_up_date__lte=week_later,follow_up_done=False).exclude(status__in=["rejected", "offered"]).order_by("follow_up_date")
    context = {"jobs":jobs,"today":today,}
    return render(request, "jobs/upcoming_followups.html", context)

@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, user=request.user)
    return render(request, 'jobs/job_detail.html',{'job':job})

@login_required
def job_create(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobForm()
    return render(request,'jobs/job_form.html',{'form':form})

@login_required
def job_update(request,pk):
    job = get_object_or_404(Job,pk=pk, user=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save(commit=False)
            if job.follow_up_date:
              job.follow_up_done = False   # enforce invariant
            job.save()
            return redirect('job_detail',pk=job.pk)
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/job_form.html',{'form':form,'job':job,'is_edit':True})

@login_required   
def job_delete(request, pk):
    job = get_object_or_404(Job,pk=pk, user=request.user)
    if request.method == 'POST':
        job.delete()
        return redirect('job_list')
    return render(request, 'jobs/job_confirm_delete.html',{'job':job})

@login_required
def export_jobs_csv(request):
    status = request.GET.get('status')
    q = request.GET.get('q')
    date_range = request.GET.get('date') #optional: 'today' or 'week'
    if request.user.is_staff:
      jobs = Job.objects.all()
    else:
      jobs = Job.objects.filter(user=request.user)


    if status in ['applied','interview','rejected','offered']:
        jobs = jobs.filter(status=status)
    if q:
        jobs = jobs.filter(Q(title__icontains=q) | Q(company__icontains=q))

    if date_range == 'today':
        today = timezone.localdate()
        jobs = jobs.filter(apply_date=today)
    elif date_range == 'week':
        today = timezone.localdate()
        start_week = today - datetime.timedelta(days=today.weekday())
        end_week = start_week + datetime.timedelta(days=6)
        jobs = jobs.filter(apply_date__range=[start_week, end_week])


    #I am sending a csv file,download it...don't show it on screen,save it as jobs.csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="jobs.csv"'

    #this object helps write rows into csv
    writer = csv.writer(response)
    #this is the first row inside csv file
    writer.writerow(['ID', 'Title', 'Company', 'Status', 'Priority','Apply Date', 'Follow-up Date', 'Next Step','Contact Name', 'Contact Email', 'Contact Phone','Job URL', 'Source','Notes', 'Rejection Reason',])
    
    #write each job as a row
    for job in jobs:
        apply_date = job.apply_date.isoformat() if getattr(job, 'apply_date', None) else ''
        follow_up = job.follow_up_date.isoformat() if getattr(job, 'follow_up_date', None) else ''
        writer.writerow([job.id,job.title,job.company,job.status,job.get_priority_display(),apply_date,follow_up,
                         job.next_step or '', job.contact_name or '',job.contact_email or '',job.contact_phone or '',
                        job.job_url or '',job.get_source_display() if getattr(job, 'source', None) else '',
                        job.notes or '', job.rejection_reason or '',])

    return response

@login_required
def stats_view(request):
    today = timezone.localdate()
    jobs = Job.objects.filter(user=request.user)

    total_all = jobs.count()
    total_applied = jobs.filter(status='applied').count()
    total_interview = jobs.filter(status='interview').count()
    total_rejected = jobs.filter(status='rejected').count()
    total_offered = jobs.filter(status='offered').count()

    follow_today = jobs.filter(follow_up_date=today, follow_up_done=False).count()
    follow_overdue = jobs.filter( follow_up_date__lt=today, follow_up_done=False).count()
    #conversion rates(avoid division by 0)
    applied_to_interview = ((total_interview/total_applied)*100 if total_applied else 0)
    interview_to_offer = ((total_offered/total_interview)*100 if total_interview else 0)
    #in_progress(pipeline:not rejected, not offered)
    in_progress = jobs.exclude(status__in=['rejected','offered']).count()
    #this week range(Mon-Sun)
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)
    applied_this_week = jobs.filter(status='applied',apply_date__range=[start_week, end_week]).count()
    #average applications per day since first apply
    first_job = jobs.order_by('apply_date').first()
    if first_job and first_job.apply_date:
        days_span = (today - first_job.apply_date).days + 1
        avg_applied_per_day = total_applied / days_span if days_span > 0 else total_applied
    else:
        avg_applied_per_day = 0

    context = {
        'today': today,
        'total_all': total_all,
        'total_applied': total_applied,
        'total_interview': total_interview,
        'total_rejected': total_rejected,
        'total_offered': total_offered,
        'follow_today': follow_today,
        'follow_overdue': follow_overdue,
        'applied_to_interview': applied_to_interview,
        'interview_to_offer': interview_to_offer,
        'in_progress': in_progress,
        'applied_this_week': applied_this_week,
        'avg_applied_per_day': avg_applied_per_day,
    }
    return render(request, 'jobs/stats.html', context)

@login_required
@require_POST
def job_quick_status(request, pk):
    job = get_object_or_404(Job, pk=pk, user=request.user)

    new_status = request.POST.get("status")
    if new_status in ["applied", "interview", "rejected", "offered"]:
        job.status = new_status
        job.save()
    return redirect(request.META.get("HTTP_REFERER", reverse("job_list")))

@login_required
@require_POST
def job_quick_priority(request, pk):
    job = get_object_or_404(Job, pk=pk, user=request.user)

    new_priority = request.POST.get("priority")
    if new_priority in ["high","medium","low"]:
        job.priority = new_priority
        job.save()
    return redirect(request.META.get("HTTP_REFERER", reverse("job_list")))

@login_required
@require_POST
def job_followup_done(request,pk):
    job = get_object_or_404(Job, pk=pk, user=request.user)
    job.follow_up_date = None
    job.follow_up_done = True  #Done ≠ Never set
    job.save()
    return HttpResponse(status=204)

@login_required
@require_POST
def job_followup_quick_update(request, pk):
    job = get_object_or_404(Job, pk=pk, user=request.user)
    date_str = request.POST.get("follow_up_date")

    if date_str:
        job.follow_up_date = datetime.date.fromisoformat(date_str)
        job.follow_up_done = False
        job.save()
    return HttpResponse(status=204)

