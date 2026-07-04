from django import forms
from .models import Job, Company, Category


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title','category','company','description','requirements','benefits',
                  'skills_required','job_type','experience_level','location','is_remote',
                  'salary_min','salary_max','salary_currency','deadline','is_featured','is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'category': forms.Select(attrs={'class':'form-control'}),
            'company': forms.Select(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':6}),
            'requirements': forms.Textarea(attrs={'class':'form-control','rows':5}),
            'benefits': forms.Textarea(attrs={'class':'form-control','rows':4}),
            'skills_required': forms.TextInput(attrs={'class':'form-control','placeholder':'Python, Django, React'}),
            'job_type': forms.Select(attrs={'class':'form-control'}),
            'experience_level': forms.Select(attrs={'class':'form-control'}),
            'location': forms.TextInput(attrs={'class':'form-control'}),
            'salary_min': forms.NumberInput(attrs={'class':'form-control'}),
            'salary_max': forms.NumberInput(attrs={'class':'form-control'}),
            'salary_currency': forms.TextInput(attrs={'class':'form-control'}),
            'deadline': forms.DateInput(attrs={'class':'form-control','type':'date'}),
        }


class JobSearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Job title or keyword'}))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Location'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label='All Categories', widget=forms.Select(attrs={'class':'form-control'}))
    job_type = forms.ChoiceField(choices=[('','All Types')]+Job.JOB_TYPES, required=False, widget=forms.Select(attrs={'class':'form-control'}))
    experience_level = forms.ChoiceField(choices=[('','All Levels')]+Job.EXP_CHOICES, required=False, widget=forms.Select(attrs={'class':'form-control'}))
    salary_min = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class':'form-control','placeholder':'Min Salary'}))
    salary_max = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class':'form-control','placeholder':'Max Salary'}))


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name','logo','website','description','location','size','industry','founded_year']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'website': forms.URLInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':4}),
            'location': forms.TextInput(attrs={'class':'form-control'}),
            'size': forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. 50-200 employees'}),
            'industry': forms.TextInput(attrs={'class':'form-control'}),
            'founded_year': forms.NumberInput(attrs={'class':'form-control'}),
        }
