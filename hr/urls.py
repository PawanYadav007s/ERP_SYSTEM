from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.hr_dashboard, name='hr_dashboard'),
    
    # Employee management
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_update, name='employee_update'),
    
    # Department management
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_update, name='department_update'),
    
    # Attendance management
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.attendance_create, name='attendance_create'),
    path('attendance/bulk/', views.bulk_attendance, name='bulk_attendance'),
    path('attendance/export/', views.export_attendance, name='export_attendance'),
    
    # Leave management
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/apply/', views.leave_apply, name='leave_apply'),
    path('leaves/<int:pk>/approve/', views.leave_approval, name='leave_approval'),
    
    # Salary management
    path('salaries/', views.salary_list, name='salary_list'),
    path('salaries/add/', views.salary_create, name='salary_create'),
    path('employees/<int:employee_id>/salary/add/', views.salary_create, name='employee_salary_create'),
    path('salaries/<int:pk>/', views.salary_detail, name='salary_detail'),
]
