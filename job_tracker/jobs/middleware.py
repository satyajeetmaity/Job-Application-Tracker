from django.shortcuts import redirect
from django.urls import reverse
import time
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate
from django.contrib.auth import logout

MAX_ATTEMPTS = 5
BLOCK_WINDOW = 180  # 3 minutes

class AdminStaffOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated:
                return redirect(reverse('login'))
            if not request.user.is_staff:
                return redirect(reverse('home'))
        return self.get_response(request)
    
class LoginRateLimitMiddleware:
    _ip_attempts = {}   # dictionary to track login attempts per IP

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/accounts/login/": # Django login URL
            ip = self.get_client_ip(request)
            now = time.time()
            attempts = self._ip_attempts.get(ip, [])

            # keep only attempts inside time window
            attempts = [t for t in attempts if now - t < BLOCK_WINDOW]
            self._ip_attempts[ip] = attempts

            if len(attempts) >= MAX_ATTEMPTS:
                return HttpResponseForbidden("Too many login attempts. Please try again after 3 minute.")
            
            #count only failed attempts
            if request.method == 'POST':
                username = request.POST.get('username')
                password = request.POST.get('password')

                user = authenticate(username=username, password=password)
                if user is None: #means Failed
                    attempts.append(now)
                    self._ip_attempts[ip] = attempts
        return self.get_response(request)
    
    def get_client_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            ip = xff.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self,request):
        if request.user.is_authenticated and not request.user.is_active:
            logout(request)
            return redirect("login")
        return self.get_response(request)