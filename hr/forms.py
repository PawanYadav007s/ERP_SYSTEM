from django import forms
from .models import Employee, Department, Attendance, Leave, Salary

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'gender', 'date_of_birth',
            'email', 'phone', 'address', 'department', 'position', 'date_joined',
            'profile_image', 'aadhar_number', 'pan_number', 'base_salary'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'time_in', 'time_out', 'status', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time_in': forms.TimeInput(attrs={'type': 'time'}),
            'time_out': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class BulkAttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].help_text = "Leave empty to enter attendance for all employees"

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

class LeaveApprovalForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['status']

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ['employee', 'effective_date', 'basic_salary', 'allowances', 'deductions', 'is_current']
        widgets = {
            'effective_date': forms.DateInput(attrs={'type': 'date'}),
        }
        