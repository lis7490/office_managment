import django_filters
from .models import Employee

class EmployeeFilter(django_filters.FilterSet):
    position = django_filters.ChoiceFilter(
        choices=Employee.PositionChoices.choices,
        field_name='position',
        lookup_expr='exact'
    )
    gender = django_filters.ChoiceFilter(
        choices=Employee.GenderChoices.choices,
        field_name='gender',
        lookup_expr='exact'
    )
    is_active = django_filters.BooleanFilter(field_name='is_active')
    
    class Meta:
        model = Employee
        fields = ['position', 'gender', 'is_active']