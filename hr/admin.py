from django.contrib import admin
from .models import Department, Employee, Attendance, Leave, Salary

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'first_name', 'last_name', 'department', 'position', 'base_salary', 'is_active']
    list_filter = ['department', 'is_active', 'gender']
    search_fields = ['first_name', 'last_name', 'employee_id', 'email']
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee_id', 'first_name', 'last_name', 'gender', 'date_of_birth', 'profile_image')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Employment Information', {
            'fields': ('department', 'position', 'date_joined', 'base_salary', 'is_active')
        }),
        ('Identity Documents', {
            'fields': ('aadhar_number', 'pan_number')
        }),
        ('System Information', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'time_in', 'time_out', 'status']
    list_filter = ['date', 'status']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    date_hierarchy = 'date'

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter = ['leave_type', 'status', 'start_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'reason']
    date_hierarchy = 'start_date'

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'effective_date', 'basic_salary', 'allowances', 'deductions', 'net_salary', 'is_current']
    list_filter = ['is_current', 'effective_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    