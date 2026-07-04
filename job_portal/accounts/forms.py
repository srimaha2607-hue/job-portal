import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from .models import User, Profile


class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email Address'}))
    role = forms.ChoiceField(choices=[('seeker','Job Seeker'),('recruiter','Recruiter')], widget=forms.Select(attrs={'class':'form-control'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}))

    class Meta:
        model = User
        fields = ['first_name','last_name','email','role']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one digit.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email'].split('@')[0] + str(User.objects.count())
        user.set_password(self.cleaned_data['password1'])
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email Address','autofocus':True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))


class OTPVerifyForm(forms.Form):
    token = forms.CharField(max_length=6, min_length=6, widget=forms.TextInput(attrs={
        'class':'form-control otp-input','placeholder':'000000','maxlength':'6','autocomplete':'off'
    }))

    def clean_token(self):
        token = self.cleaned_data.get('token','').strip()
        if not token.isdigit():
            raise ValidationError('OTP must be 6 digits.')
        return token


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = Profile
        fields = ['avatar','bio','phone','location','website','linkedin','github','skills',
                  'experience_years','company_name','company_website','company_description']
        widgets = {
            'bio': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'phone': forms.TextInput(attrs={'class':'form-control'}),
            'location': forms.TextInput(attrs={'class':'form-control'}),
            'website': forms.URLInput(attrs={'class':'form-control'}),
            'linkedin': forms.URLInput(attrs={'class':'form-control'}),
            'github': forms.URLInput(attrs={'class':'form-control'}),
            'skills': forms.TextInput(attrs={'class':'form-control','placeholder':'Python, Django, JavaScript'}),
            'experience_years': forms.NumberInput(attrs={'class':'form-control'}),
            'company_name': forms.TextInput(attrs={'class':'form-control'}),
            'company_website': forms.URLInput(attrs={'class':'form-control'}),
            'company_description': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['resume']
        widgets = {'resume': forms.FileInput(attrs={'class':'form-control','accept':'.pdf,.doc,.docx'})}

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            ext = '.' + resume.name.rsplit('.',1)[-1].lower()
            if ext not in ['.pdf','.doc','.docx']:
                raise ValidationError('Only PDF, DOC, DOCX files allowed.')
            if resume.size > 10 * 1024 * 1024:
                raise ValidationError('File size must be under 10MB.')
        return resume


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter your email'}))


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
