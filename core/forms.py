from django import forms
from django.core.exceptions import ValidationError
from .models import UploadedFile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UploadFileForm(forms.ModelForm):
    prompt = forms.CharField(
        widget=forms.Textarea(attrs={'maxlength': 250, 'rows': 4}),
        max_length=250,
        label='Prompt',
    )

    class Meta:
        model = UploadedFile
        fields = ['prompt', 'file']

    def clean_file(self):
        file = self.cleaned_data['file']
        file_extension = file.name.split('.')[-1].lower()

        # Check if the file extension is either csv or xlsx
        if file_extension not in ('csv', 'xlsx'):
            raise ValidationError("Unsupported file format. Please upload a csv or xlsx file.")

        return file
