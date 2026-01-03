import django
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Job


@staff_member_required
def admin_dashboard(request):

    total_users = User.objects.count()
    total_jobs = Job.objects.count()

    # Status breakdown
    status_stats = Job.objects.values('status').annotate(count=Count('status'))

    # Top companies
    top_companies = Job.objects.values('company').annotate(count=Count('company')).order_by('-count')[:5]

    # Active user count - logged in last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_users = User.objects.filter(last_login__gte=thirty_days_ago).count()

    # Users with no jobs
    users_with_no_jobs = total_users - Job.objects.values('user').distinct().count()

    # Follow-ups summary
    today = timezone.now().date()
    follow_today = Job.objects.filter(follow_up_date=today, follow_up_done=False).count()
    follow_overdue = Job.objects.filter(follow_up_date__lt=today, follow_up_done=False).count()

    context = {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "active_users": active_users,
        "users_with_no_jobs": users_with_no_jobs,
        "status_stats": status_stats,
        "top_companies": top_companies,
        "follow_today": follow_today,
        "follow_overdue": follow_overdue,
    }

    return render(request, "jobs/admin_dashboard.html", context)

@staff_member_required
def admin_job_list(request):
    jobs = Job.objects.select_related("user")
    
    #filters
    status = request.GET.get("status")
    user_id = request.GET.get("user")
    q = request.GET.get("q")
    follow = request.GET.get("follow")

    if status:
        jobs = jobs.filter(status=status)
    if user_id:
        jobs = jobs.filter(user_id=user_id)
    if q:
        jobs = jobs.filter(Q(title__icontains=q) | Q(company__icontains=q) | Q(user__username__icontains=q))

    today = timezone.localdate()
    if follow == "today":
        jobs = jobs.filter(follow_up_date=today, follow_up_done=False)
    elif follow == "overdue":
        jobs = jobs.filter(follow_up_date__lt=today, follow_up_done=False)

    users = User.objects.all().order_by("username")

    context = {"jobs": jobs.order_by("-id"), "users": users, "current_staus": status, "current_user": user_id, "current_q": q, "current_follow": follow}
    return render(request, "jobs/admin_job_list.html", context)