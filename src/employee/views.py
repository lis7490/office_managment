from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Employee

def home(request):
    total_employees = Employee.objects.count()
    latest_employees = Employee.objects.order_by('-hire_date')[:4]
    
    context = {
        'total_employees': total_employees,
        'latest_employees': latest_employees,
    }
    return render(request, 'employees/home.html', context)

def employee_list(request):
    employees_list = Employee.objects.all().prefetch_related('images', 'skills').order_by('-hire_date')
    
    paginator = Paginator(employees_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'employees/employee_list.html', context)

def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    context = {
        'employee': employee,
    }
    return render(request, 'employees/employee_detail.html', context)