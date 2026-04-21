from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from .models import Profile


phone_validator = RegexValidator(
    regex=r"^\d{7,15}$",
    message="Phone number must contain only digits and be 7 to 15 characters long.",
)

class BaseRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class SeekerRegistrationForm(BaseRegistrationForm):
    phone_number = forms.CharField(max_length=20, required=False, validators=[phone_validator])
    profile_photo = forms.ImageField(required=False)
    current_job_title = forms.CharField(max_length=150, required=False)
    years_of_experience = forms.IntegerField(required=False, min_value=0)
    primary_skills = forms.CharField(max_length=255, required=False)
    seeker_industry = forms.CharField(max_length=100, required=False)
    education = forms.CharField(max_length=100, required=False)
    resume = forms.FileField(required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    
    JOB_TYPES = [('Full-time', 'Full-time'), ('Part-time', 'Part-time'), ('Freelance', 'Freelance'), ('Internship', 'Internship')]
    job_type = forms.ChoiceField(choices=[('', '---')] + JOB_TYPES, required=False)
    
    WORK_MODES = [('Remote', 'Remote'), ('On-site', 'On-site'), ('Hybrid', 'Hybrid')]
    work_mode = forms.ChoiceField(choices=[('', '---')] + WORK_MODES, required=False)
    
    expected_salary = forms.CharField(max_length=100, required=False)
    notice_period = forms.CharField(max_length=100, required=False)

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if not resume:
            return resume
        name = (resume.name or '').lower()
        if not name.endswith('.pdf'):
            raise forms.ValidationError('Only PDF files are allowed for CV upload.')
        content_type = getattr(resume, 'content_type', None)
        if content_type and content_type != 'application/pdf':
            raise forms.ValidationError('Uploaded CV must be a valid PDF file.')
        return resume

    def save_profile(self, user):
        profile = user.profile
        profile.role = Profile.Role.SEEKER
        profile.phone_number = self.cleaned_data.get('phone_number', '')
        profile.bio = self.cleaned_data.get('bio', '')
        if self.cleaned_data.get('profile_photo'):
            profile.profile_photo = self.cleaned_data['profile_photo']
        profile.current_job_title = self.cleaned_data.get('current_job_title', '')
        profile.years_of_experience = self.cleaned_data.get('years_of_experience')
        profile.primary_skills = self.cleaned_data.get('primary_skills', '')
        profile.seeker_industry = self.cleaned_data.get('seeker_industry', '')
        profile.education = self.cleaned_data.get('education', '')
        if self.cleaned_data.get('resume'):
            profile.resume = self.cleaned_data['resume']
        profile.job_type = self.cleaned_data.get('job_type', '')
        profile.work_mode = self.cleaned_data.get('work_mode', '')
        profile.expected_salary = self.cleaned_data.get('expected_salary', '')
        profile.notice_period = self.cleaned_data.get('notice_period', '')
        profile.save()

class ProviderRegistrationForm(BaseRegistrationForm):
    phone_number = forms.CharField(max_length=20, required=False, validators=[phone_validator])
    company_name = forms.CharField(max_length=150, required=True)
    company_logo = forms.ImageField(required=False)
    company_industry = forms.CharField(max_length=100, required=False)
    
    COMPANY_SIZES = [('1-10', '1-10'), ('11-50', '11-50'), ('51-200', '51-200'), ('200+', '200+')]
    company_size = forms.ChoiceField(choices=[('', '---')] + COMPANY_SIZES, required=False)
    
    company_website = forms.URLField(required=False)
    company_location = forms.CharField(max_length=200, required=False)
    company_description = forms.CharField(widget=forms.Textarea, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    recruiter_designation = forms.CharField(max_length=100, required=False)
    linkedin_profile = forms.URLField(required=False)

    def save_profile(self, user):
        profile = user.profile
        profile.role = Profile.Role.PROVIDER
        profile.phone_number = self.cleaned_data.get('phone_number', '')
        profile.bio = self.cleaned_data.get('bio', '')
        profile.company_name = self.cleaned_data.get('company_name', '')
        if self.cleaned_data.get('company_logo'):
            profile.company_logo = self.cleaned_data['company_logo']
        profile.company_industry = self.cleaned_data.get('company_industry', '')
        profile.company_size = self.cleaned_data.get('company_size', '')
        profile.company_website = self.cleaned_data.get('company_website', '')
        profile.company_location = self.cleaned_data.get('company_location', '')
        profile.company_description = self.cleaned_data.get('company_description', '')
        profile.recruiter_designation = self.cleaned_data.get('recruiter_designation', '')
        profile.linkedin_profile = self.cleaned_data.get('linkedin_profile', '')
        profile.save()


class BaseProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ['phone_number', 'bio', 'location']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def clean_phone_number(self):
        value = (self.cleaned_data.get('phone_number') or '').strip()
        if value:
            phone_validator(value)
        return value

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data['email']
        if commit:
            user.save(update_fields=['first_name', 'last_name', 'email'])
            profile.save()
        return profile


class SeekerProfileUpdateForm(BaseProfileUpdateForm):
    class Meta(BaseProfileUpdateForm.Meta):
        fields = BaseProfileUpdateForm.Meta.fields + [
            'profile_photo',
            'current_job_title',
            'years_of_experience',
            'primary_skills',
            'seeker_industry',
            'education',
            'resume',
            'job_type',
            'work_mode',
            'expected_salary',
            'notice_period',
        ]

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if not resume:
            return resume
        name = (resume.name or '').lower()
        if not name.endswith('.pdf'):
            raise forms.ValidationError('Only PDF files are allowed for CV upload.')
        content_type = getattr(resume, 'content_type', None)
        if content_type and content_type != 'application/pdf':
            raise forms.ValidationError('Uploaded CV must be a valid PDF file.')
        return resume


class ProviderProfileUpdateForm(BaseProfileUpdateForm):
    class Meta(BaseProfileUpdateForm.Meta):
        fields = BaseProfileUpdateForm.Meta.fields + [
            'company_name',
            'company_logo',
            'company_industry',
            'company_size',
            'company_website',
            'company_location',
            'company_description',
            'recruiter_designation',
            'linkedin_profile',
        ]
