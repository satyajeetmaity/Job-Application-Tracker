from django.shortcuts import redirect
from django.urls import reverse

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