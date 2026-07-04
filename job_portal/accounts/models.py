import os
import pyotp
import shortuuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_RECRUITER = 'recruiter'
    ROLE_SEEKER = 'seeker'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_RECRUITER, 'Recruiter'),
        (ROLE_SEEKER, 'Job Seeker'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_SEEKER)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_recruiter(self):
        return self.role == self.ROLE_RECRUITER

    @property
    def is_seeker(self):
        return self.role == self.ROLE_SEEKER


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    skills = models.TextField(blank=True, help_text='Comma-separated skills')
    experience_years = models.PositiveIntegerField(default=0)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    resume_original_name = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    company_website = models.URLField(blank=True)
    company_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.email}"

    @property
    def skills_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'


class OTPDevice(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp_device')
    secret = models.CharField(max_length=64)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP Device for {self.user.email}"

    def get_totp(self):
        return pyotp.TOTP(self.secret)

    def verify_token(self, token):
        totp = self.get_totp()
        return totp.verify(str(token).strip(), valid_window=2)

    def get_provisioning_uri(self):
        totp = self.get_totp()
        return totp.provisioning_uri(
            name=self.user.email,
            issuer_name='Job Portal'
        )
    @classmethod
    def create_for_user(cls, user):
        try:
            device = cls.objects.get(user=user)
        except cls.DoesNotExist:
            device = cls.objects.create(
                user=user,
                secret=pyotp.random_base32(),
                is_verified=False,
            )
            
        return device
class RecoveryCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recovery_codes')
    code = models.CharField(max_length=20)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recovery code for {self.user.email}"

    @classmethod
    def generate_codes(cls, user, count=8):
        cls.objects.filter(user=user).delete()
        codes = []
        for _ in range(count):
            code = shortuuid.uuid()[:10].upper()
            codes.append(cls(user=user, code=code))
        cls.objects.bulk_create(codes)
        return [c.code for c in codes]
