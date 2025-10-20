import django_filters
from .models import Employee

class EmployeeFilter(django_filters.FilterSet):
    skills = django_filters.CharFilter(field_name='skills__name', lookup_expr='icontains')
    min_experience_days = django_filters.NumberFilter(method='filter_min_experience')
    max_experience_days = django_filters.NumberFilter(method='filter_max_experience')
    position = django_filters.ChoiceFilter(choices=Employee.POSITION_CHOICES)
    gender = django_filters.ChoiceFilter(choices=Employee.GENDER_CHOICES)  # Теперь будет работать
    desk_number = django_filters.NumberFilter()
    
    class Meta:
        model = Employee
        fields = ['skills', 'position', 'gender', 'desk_number']
    
    def filter_min_experience(self, queryset, name, value):
        """
        Фильтр по минимальному стажу (в днях)
        """
        from django.utils import timezone
        from datetime import timedelta
        
        min_hire_date = timezone.now().date() - timedelta(days=int(value))
        return queryset.filter(hire_date__lte=min_hire_date)
    
    def filter_max_experience(self, queryset, name, value):
        """
        Фильтр по максимальному стажу (в днях)
        """
        from django.utils import timezone
        from datetime import timedelta
        
        max_hire_date = timezone.now().date() - timedelta(days=int(value))
        return queryset.filter(hire_date__gte=max_hire_date)