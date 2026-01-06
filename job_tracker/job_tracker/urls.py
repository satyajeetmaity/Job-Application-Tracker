"""
URL configuration for job_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from jobs.views import signup, verify_email, home, job_list, job_detail, job_create, job_update, job_delete, export_jobs_csv, followup_list, upcoming_followups, stats_view, job_quick_status, job_quick_priority, job_followup_done, job_followup_quick_update
from jobs.views_admin import admin_dashboard, admin_job_list, admin_activity_timeline, admin_toggle_user_active

urlpatterns = [
    path('admin/', admin.site.urls),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/jobs/", admin_job_list, name="admin_job_list"),
    path("admin-dashboard/activity/", admin_activity_timeline, name="admin_activity_timeline"),
    path("admin-dashboard/users/<int:user_id>/toggle/", admin_toggle_user_active,name="admin_toggle_user_active"),
    
    path('accounts/', include('django.contrib.auth.urls')),

    path('signup/', signup, name='signup'),
    path('verify/<int:user_id>/<str:token>/', verify_email, name='verify_email'),

    path('password_reset/',auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    path('', home, name='home'),
    path('jobs/', job_list, name='job_list'),
    path('jobs/add/', job_create, name='job_create'),
    path('jobs/<int:pk>/', job_detail, name='job_detail'),
    path('jobs/<int:pk>/edit/', job_update, name='job_update'),
    path('jobs/<int:pk>/delete/', job_delete, name='job_delete'),
    path('jobs/export/csv/', export_jobs_csv, name='export_jobs_csv'),
    path('jobs/followups/', followup_list, name='followup_list'),
    path('jobs/followups/upcoming/', upcoming_followups, name='upcoming_followups'),
    path('jobs/stats/', stats_view, name='stats'),
    path('jobs/<int:pk>/status/', job_quick_status, name='job_quick_status'),
    path('jobs/<int:pk>/priority/', job_quick_priority, name='job_quick_priority'),
    path('jobs/<int:pk>/followup/done/', job_followup_done, name='job_followup_done'),
    path('jobs/<int:pk>/followup/quick/', job_followup_quick_update, name='job_followup_quick_update'),
]
