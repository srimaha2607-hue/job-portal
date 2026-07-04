import io
import qrcode
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy
from .models import User, Profile, OTPDevice, RecoveryCode
from .forms import RegisterForm, LoginForm, OTPVerifyForm, ProfileForm, ResumeUploadForm, CustomPasswordResetForm, CustomSetPasswordForm
from notifications.models import Notification


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            token = get_random_string(48)
            user.email_verification_token = token
            user.save()
            messages.success(request, 'Account created! Please check your email to verify your account.')
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.two_factor_enabled:
                request.session['pre_2fa_user_id'] = user.id
                return redirect('accounts:verify_otp')
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome back, {user.full_name}!')
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def verify_otp(request):
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return redirect('accounts:login')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            try:
                device = user.otp_device
                if device.verify_token(token):
                    del request.session['pre_2fa_user_id']
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    request.session['2fa_verified'] = True
                    request.session.modified = True
                    messages.success(request, f'Welcome back, {user.full_name}!')
                    return redirect('dashboard:index')
                else:
                    messages.error(request, 'Invalid OTP. Please try again.')
            except OTPDevice.DoesNotExist:
                messages.error(request, 'OTP device not found.')
        # Check recovery code
        recovery_code = request.POST.get('recovery_code', '').strip().upper()
        if recovery_code:
            rc = RecoveryCode.objects.filter(user=user, code=recovery_code, is_used=False).first()
            if rc:
                rc.is_used = True
                rc.save()
                del request.session['pre_2fa_user_id']
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.warning(request, 'Logged in using recovery code. Please review your 2FA settings.')
                return redirect('dashboard:index')
            else:
                messages.error(request, 'Invalid recovery code.')
    else:
        form = OTPVerifyForm()
    return render(request, 'accounts/verify_otp.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('jobs:home')


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            profile_obj = form.save()
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile_obj, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        })
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile_obj})


@login_required
def upload_resume(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            p = form.save(commit=False)
            if 'resume' in request.FILES:
                p.resume_original_name = request.FILES['resume'].name
            p.save()
            messages.success(request, 'Resume uploaded successfully!')
        else:
            messages.error(request, 'Invalid file. Only PDF/DOC/DOCX allowed under 10MB.')
    return redirect('accounts:profile')


@login_required
def setup_2fa(request):
    device = OTPDevice.create_for_user(request.user)
    print("DEVICE:", device)
    print("TYPE:", type(device))
    uri = device.get_provisioning_uri()
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            print("TOKEN:",token)
            print("SECRET:", device.secret)
            print("VERIFY:", device.verify_token(token))
            if device.verify_token(token):
                device.is_verified = True
                device.save()
                request.user.two_factor_enabled = True
                request.user.save()
                codes = RecoveryCode.generate_codes(request.user)
                messages.success(request, '2FA enabled successfully!')
                return render(request, 'accounts/2fa_recovery_codes.html', {'codes': codes})
            else:
                messages.error(request, 'Invalid OTP. Please scan the QR code again.')
    else:
        form = OTPVerifyForm()
    return render(request, 'accounts/setup_2fa.html', {
        'form': form, 'qr_code': qr_b64, 'secret': device.secret, 'device': device
    })


@login_required
def disable_2fa(request):
    if request.method == 'POST':
        token = request.POST.get('token','')
        try:
            device = request.user.otp_device
            if device.verify_token(token):
                request.user.two_factor_enabled = False
                request.user.save()
                messages.success(request, '2FA disabled.')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Invalid OTP.')
        except OTPDevice.DoesNotExist:
            messages.error(request, 'No 2FA device found.')
    return render(request, 'accounts/disable_2fa.html')


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/emails/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
