from django import forms
from django.core.exceptions import ValidationError
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