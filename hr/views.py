from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from .models import Employee, Department, Attendance, Leave, Salary
from .forms import (
    EmployeeForm, DepartmentForm, AttendanceForm, BulkAttendanceForm,
    LeaveForm, LeaveApprovalForm, SalaryForm
)
import datetime
import csv

@login_required
def hr_dashboard(request):
    total_employees = Employee.objects.filter(is_active=True).count()
    departments = Department.objects.all()
    recent_leaves = Leave.objects.filter(status='pending').order_by('-created_at')[:5]
    
    # Today's attendance
    today = datetime.date.today()
    today_attendance = Attendance.objects.filter(date=today)
    present_count = today_attendance.filter(status='present').count()
    absent_count = today_attendance.filter(status='absent').count()
    
    context = {
        'total_employees': total_employees,
        'departments': departments,
        'recent_leaves': recent_leaves,
        'present_count': present_count,
        'absent_count': absent_count,
    }
    return render(request, 'hr/dashboard.html', context)

# Employee views
@login_required
def employee_list(request):
    search_query = request.GET.get('search', '')
    department_id = request.GET.get('department', '')
    
    employees = Employee.objects.all()
    
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    departments = Department.objects.all()
    
    context = {
        'employees': employees,
        'departments': departments,
        'search_query': search_query,
        'selected_department': department_id
    }
    return render(request, 'hr/employee_list.html', context)

@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    current_salary = Salary.objects.filter(employee=employee, is_current=True).first()
    attendance_records = Attendance.objects.filter(employee=employee).order_by('-date')[:10]
    leave_records = Leave.objects.filter(employee=employee).order_by('-start_date')[:5]
    
    context = {
        'employee': employee,
        'current_salary': current_salary,
        'attendance_records': attendance_records,
        'leave_records': leave_records,
    }
    return render(request, 'hr/employee_detail.html', context)

@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()
            messages.success(request, 'Employee created successfully!')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm()
    
    return render(request, 'hr/employee_form.html', {
        'form': form,
        'title': 'Add New Employee'
    })

@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee information updated successfully!')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'hr/employee_form.html', {
        'form': form,
        'employee': employee,
        'title': 'Edit Employee'
    })

# Department views
@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'hr/department_list.html', {'departments': departments})

@login_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, 'Department created successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    
    return render(request, 'hr/department_form.html', {'form': form, 'title': 'Add Department'})

@login_required
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'hr/department_form.html', {
        'form': form,
        'department': department,
        'title': 'Edit Department'
    })

# Attendance views
@login_required
def attendance_list(request):
    start_date = request.GET.get('start_date', (datetime.date.today() - datetime.timedelta(days=7)).isoformat())
    end_date = request.GET.get('end_date', datetime.date.today().isoformat())
    employee_id = request.GET.get('employee', '')
    
    attendances = Attendance.objects.filter(date__range=[start_date, end_date])
    
    if employee_id:
        attendances = attendances.filter(employee_id=employee_id)
    
    attendances = attendances.order_by('-date', 'employee__first_name')
    
    employees = Employee.objects.filter(is_active=True)
    
    context = {
        'attendances': attendances,
        'employees': employees,
        'start_date': start_date,
        'end_date': end_date,
        'selected_employee': employee_id
    }
    return render(request, 'hr/attendance_list.html', context)

@login_required
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance recorded successfully!')
            return redirect('attendance_list')
    else:
        form = AttendanceForm(initial={'date': datetime.date.today()})
    
    return render(request, 'hr/attendance_form.html', {'form': form})

@login_required
def bulk_attendance(request):
    if request.method == 'POST':
        form = BulkAttendanceForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            department = form.cleaned_data['department']
            
            # Get employees based on department filter
            if department:
                employees = Employee.objects.filter(department=department, is_active=True)
            else:
                employees = Employee.objects.filter(is_active=True)
            
            # Process attendance data from form
            for employee in employees:
                status = request.POST.get(f'status_{employee.id}')
                time_in = request.POST.get(f'time_in_{employee.id}')
                time_out = request.POST.get(f'time_out_{employee.id}')
                notes = request.POST.get(f'notes_{employee.id}', '')
                
                if status:  # Only create if status is provided
                    # Check if attendance record exists
                    attendance, created = Attendance.objects.get_or_create(
                        employee=employee, 
                        date=date,
                        defaults={
                            'status': status,
                            'time_in': time_in or '09:00',  # Default values
                            'time_out': time_out,
                            'notes': notes
                        }
                    )
                    
                    # If record exists, update it
                    if not created:
                        attendance.status = status
                        if time_in:
                            attendance.time_in = time_in
                        if time_out:
                            attendance.time_out = time_out
                        attendance.notes = notes
                        attendance.save()
            
            messages.success(request, 'Attendance recorded successfully for all employees!')
            return redirect('attendance_list')
            
    else:
        form = BulkAttendanceForm

# Continue from where we left off in the views.py file

@login_required
def bulk_attendance(request):
    if request.method == 'POST':
        form = BulkAttendanceForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            department = form.cleaned_data['department']
            
            # Get employees based on department filter
            if department:
                employees = Employee.objects.filter(department=department, is_active=True)
            else:
                employees = Employee.objects.filter(is_active=True)
            
            # Process attendance data from form
            for employee in employees:
                status = request.POST.get(f'status_{employee.id}')
                time_in = request.POST.get(f'time_in_{employee.id}')
                time_out = request.POST.get(f'time_out_{employee.id}')
                notes = request.POST.get(f'notes_{employee.id}', '')
                
                if status:  # Only create if status is provided
                    # Check if attendance record exists
                    attendance, created = Attendance.objects.get_or_create(
                        employee=employee, 
                        date=date,
                        defaults={
                            'status': status,
                            'time_in': time_in or '09:00',  # Default values
                            'time_out': time_out,
                            'notes': notes
                        }
                    )
                    
                    # If record exists, update it
                    if not created:
                        attendance.status = status
                        if time_in:
                            attendance.time_in = time_in
                        if time_out:
                            attendance.time_out = time_out
                        attendance.notes = notes
                        attendance.save()
            
            messages.success(request, 'Attendance recorded successfully for all employees!')
            return redirect('attendance_list')
    else:
        form = BulkAttendanceForm(initial={'date': datetime.date.today()})
    
    # If department is selected, show employees for that department
    if request.method == 'POST' and form.is_valid():
        department = form.cleaned_data['department']
        if department:
            employees = Employee.objects.filter(department=department, is_active=True)
        else:
            employees = Employee.objects.filter(is_active=True)
    else:
        employees = Employee.objects.filter(is_active=True)
    
    context = {
        'form': form,
        'employees': employees
    }
    return render(request, 'hr/bulk_attendance.html', context)

@login_required
def export_attendance(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    employee_id = request.GET.get('employee')
    
    # Filter attendance records
    attendances = Attendance.objects.all().order_by('date', 'employee__first_name')
    
    if start_date and end_date:
        attendances = attendances.filter(date__range=[start_date, end_date])
    
    if employee_id:
        attendances = attendances.filter(employee_id=employee_id)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Employee ID', 'Employee Name', 'Time In', 'Time Out', 'Status', 'Notes'])
    
    for attendance in attendances:
        writer.writerow([
            attendance.date,
            attendance.employee.employee_id,
            f"{attendance.employee.first_name} {attendance.employee.last_name}",
            attendance.time_in,
            attendance.time_out or '',
            attendance.get_status_display(),
            attendance.notes or ''
        ])
    
    return response

# Leave views
@login_required
def leave_list(request):
    status = request.GET.get('status', '')
    
    # Different views for HR and employees
    if request.user.is_staff:  # HR staff can see all leaves
        leaves = Leave.objects.all()
        if status:
            leaves = leaves.filter(status=status)
        leaves = leaves.order_by('-created_at')
    else:  # Regular employees can only see their own leaves
        if hasattr(request.user, 'employee'):
            employee = request.user.employee
            leaves = Leave.objects.filter(employee=employee)
            if status:
                leaves = leaves.filter(status=status)
            leaves = leaves.order_by('-created_at')
        else:
            leaves = Leave.objects.none()
    
    context = {
        'leaves': leaves,
        'status_filter': status
    }
    return render(request, 'hr/leave_list.html', context)

@login_required
def leave_apply(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.status = 'pending'
            leave.save()
            messages.success(request, 'Leave application submitted successfully!')
            return redirect('leave_list')
    else:
        # Pre-fill employee if it's a regular employee
        employee = None
        if hasattr(request.user, 'employee'):
            employee = request.user.employee
            form = LeaveForm(initial={'employee': employee})
        else:
            form = LeaveForm()
    
    return render(request, 'hr/leave_form.html', {'form': form})

@login_required
def leave_approval(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    
    if request.method == 'POST':
        form = LeaveApprovalForm(request.POST, instance=leave)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.approved_by = request.user
            leave.save()
            messages.success(request, f'Leave application {leave.get_status_display()} successfully!')
            return redirect('leave_list')
    else:
        form = LeaveApprovalForm(instance=leave)
    
    context = {
        'form': form,
        'leave': leave
    }
    return render(request, 'hr/leave_approval.html', context)

# Salary views
@login_required
def salary_list(request):
    employee_id = request.GET.get('employee', '')
    
    if employee_id:
        salaries = Salary.objects.filter(employee_id=employee_id).order_by('-effective_date')
    else:
        salaries = Salary.objects.filter(is_current=True).order_by('employee__first_name')
    
    employees = Employee.objects.filter(is_active=True)
    
    context = {
        'salaries': salaries,
        'employees': employees,
        'selected_employee': employee_id
    }
    return render(request, 'hr/salary_list.html', context)

@login_required
def salary_create(request, employee_id=None):
    if employee_id:
        employee = get_object_or_404(Employee, pk=employee_id)
        initial_data = {
            'employee': employee,
            'basic_salary': employee.base_salary,
        }
    else:
        initial_data = {}
    
    if request.method == 'POST':
        form = SalaryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salary information saved successfully!')
            return redirect('salary_list')
    else:
        form = SalaryForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Add Salary Information'
    }
    
    if employee_id:
        context['employee'] = get_object_or_404(Employee, pk=employee_id)
    
    return render(request, 'hr/salary_form.html', context)

@login_required
def salary_detail(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    
    context = {
        'salary': salary,
    }
    return render(request, 'hr/salary_detail.html', context)