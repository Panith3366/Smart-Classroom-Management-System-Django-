from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import CustomUser, AdminProfile, TeacherProfile, StudentProfile, ParentProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'date_of_birth', 'address', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Customize role choices based on permissions
        self.fields['role'].widget.attrs['class'] = 'form-select'
        
        # Set default passwords based on role
        if not args or not args[0]:  # Only set defaults for new forms (not when processing POST data)
            # Set default password placeholders
            self.fields['password1'].widget.attrs['placeholder'] = 'Default: admin123/student123/teacher123 based on role'
            self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'
            
            # Add JavaScript to auto-fill passwords based on role selection
            self.fields['role'].widget.attrs['onchange'] = 'updateDefaultPassword(this.value)'
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        # Set default passwords if fields are empty
        if not password1 and not password2:
            if role == 'admin':
                cleaned_data['password1'] = 'admin123'
                cleaned_data['password2'] = 'admin123'
            elif role == 'student':
                cleaned_data['password1'] = 'student123'
                cleaned_data['password2'] = 'student123'
            elif role == 'teacher':
                cleaned_data['password1'] = 'teacher123'
                cleaned_data['password2'] = 'teacher123'
            elif role == 'parent':
                cleaned_data['password1'] = 'parent123'
                cleaned_data['password2'] = 'parent123'
        
        return cleaned_data

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = ['department', 'permissions_level']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'permissions_level': forms.Select(attrs={'class': 'form-select'}),
        }

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['department', 'qualification', 'experience_years', 'specialization', 
                 'hire_date', 'salary', 'emergency_contact_name', 'emergency_contact_phone']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['roll_number', 'grade', 'classroom', 'admission_date', 
                 'parent_guardian_name', 'parent_guardian_phone', 'parent_guardian_email',
                 'emergency_contact_name', 'emergency_contact_phone', 'medical_conditions', 'blood_group']
        widgets = {
            'roll_number': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'classroom': forms.Select(attrs={'class': 'form-select'}),
            'admission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'parent_guardian_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_guardian_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_guardian_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ParentProfileForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = ['students', 'relationship', 'occupation', 'workplace', 'work_phone']
        widgets = {
            'students': forms.CheckboxSelectMultiple(),
            'relationship': forms.Select(attrs={'class': 'form-select'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'workplace': forms.TextInput(attrs={'class': 'form-control'}),
            'work_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'address', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class StudentCredentialLoginForm(forms.Form):
    """Special form for parents to login with student credentials"""
    student_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Student ID'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Student Password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        student_id = cleaned_data.get('student_id')
        password = cleaned_data.get('password')
        
        if student_id and password:
            try:
                student_profile = StudentProfile.objects.get(student_id=student_id)
                user = authenticate(username=student_profile.user.username, password=password)
                if not user:
                    raise forms.ValidationError("Invalid student credentials.")
                if user.role != 'student':
                    raise forms.ValidationError("Invalid student account.")
                cleaned_data['student_user'] = user
            except StudentProfile.DoesNotExist:
                raise forms.ValidationError("Student ID not found.")
        
        return cleaned_data