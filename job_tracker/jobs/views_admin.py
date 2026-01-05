import django
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Job, AdminActivity


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
    mode = request.GET.get("mode", "jobs")
    context = {"mode": mode}
    
    if mode == "jobs":
         jobs = Job.objects.select_related("user")
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

         context.update({"jobs": jobs.order_by("-id"), "users": User.objects.all().order_by("username"), "current_staus": status, "current_user": user_id, "current_q": q, "current_follow": follow})
    elif mode == "users":
         context["users"] = (User.objects.annotate(job_count=Count("job")).order_by("username"))
    elif mode == "no_jobs":
         context["users"] = (User.objects.annotate(job_count=Count("job")).filter(job_count=0).order_by("username"))
    return render(request, "jobs/admin_job_list.html", context)

@staff_member_required
def admin_activity_timeline(request):
    activities = AdminActivity.objects.select_related("user", "job").order_by("-created_at")
    user_id = request.GET.get("user")
    action = request.GET.get("action")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if user_id:
        activities = activities.filter(user_id=user_id)
    if action:
        activities = activities.filter(action=action)
    if date_from:
        activities = activities.filter(created_at__date__gte=date_from)
    if date_to:
        activities = activities.filter(created_at__date__lte=date_to)
    context = {
        "activities": activities[:200],  # safety limit
        "users": User.objects.order_by("username"),
        "actions": AdminActivity.ACTION_CHOICES,
        "current_user": user_id,
        "current_action": action,
        "current_from": date_from,
        "current_to": date_to,
    }
    return render(request, "jobs/admin_activity_timeline.html", context)