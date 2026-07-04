from django.shortcuts import redirect
from django.urls import reverse

EXEMPT_URLS = [
    '/accounts/login/', '/accounts/logout/', '/accounts/register/',
    '/accounts/verify-otp/', '/accounts/password-reset/',
    '/static/', '/media/', '/admin/',
]

class TwoFactorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.two_factor_enabled:
            path = request.path_info
            exempt = any(path.startswith(u) for u in EXEMPT_URLS)

            if not exempt and not request.session.get('2fa_verified'):
                return redirect('accounts:verify_otp')

        return self.get_response(request)
