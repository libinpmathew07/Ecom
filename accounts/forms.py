from django import forms 
from.models import Account
from django.forms.widgets import PasswordInput

class RegistrationForm(forms.ModelForm):
    password=forms.CharField(widget=PasswordInput(attrs={
        'placeholder':"Enter password",
        'class':'form-control'
    }))
    confirm_password=forms.CharField(widget=PasswordInput(attrs={
        'placeholder':"Confirm password",
        'class':'form-control'
    }))
    class Meta:
        model=Account
        fields=['first_name','password','email','last_name','phone_number']

    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder']='first name'
        # self.fields[last_name].widget.attrs['placeholder']='last name'
        # self.fields[email].widget.attrs['placeholder']='email'
        # self.fields[phone_number].widget.attrs['placeholder']='phone number'
        for field in self.fields:
            self.fields[field].widget.attrs['class']='forms-control'

    def clean(self):
        cleaned_data= super(RegistrationForm,self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')

        if password!=confirm_password:
            raise forms.ValidationError("Password does not match")
        