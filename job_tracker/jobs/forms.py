from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Job

class JobForm(forms.ModelForm):
    apply_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    follow_up_date = forms.DateField(required=False,widget=forms.DateInput(attrs={'type':'date'}))
    class Meta:
        model = Job
        fields = ['title','company','status','apply_date','priority','follow_up_date','next_step','contact_name','contact_email','contact_phone','job_url','source','salary_min','salary_max','rejection_reason','notes']

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')

        if status != 'rejected' and rejection_reason:
            raise ValidationError("Rejection reason is only allowed when status is 'Rejected'.")
        return cleaned_data
    
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email
