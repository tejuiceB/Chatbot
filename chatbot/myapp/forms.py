from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Appointment, Blog

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    age = forms.IntegerField()
    profile_picture = forms.ImageField(required=False)
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPES)
    
    # Doctor specific fields
    specialization = forms.CharField(max_length=100, required=False)
    experience = forms.IntegerField(required=False)
    available_times = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'phone', 'address', 'age', 
                 'profile_picture', 'specialization', 'experience', 'available_times', 
                 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make doctor fields initially hidden
        self.fields['specialization'].widget.attrs['class'] = 'doctor-field'
        self.fields['experience'].widget.attrs['class'] = 'doctor-field'
        self.fields['available_times'].widget.attrs['class'] = 'doctor-field'

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'notes']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content']