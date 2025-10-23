from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views  # Импортируем API views
from . import views      # Импортируем обычные views

# Router для API
router = DefaultRouter()
router.register('employees', api_views.EmployeeViewSet, basename='employees')
router.register('desks', api_views.DeskViewSet, basename='desks')
router.register('skills', api_views.SkillViewSet, basename='skills')
router.register('employee-skills', api_views.EmployeeSkillViewSet, basename='employee-skills')
router.register('employee-images', api_views.EmployeeImageViewSet, basename='employee-images')

urlpatterns = [
    # HTML routes
    path('', views.employee_list, name='employee_list'),
    path('<int:pk>/', views.employee_detail, name='employee_detail'),
    
    # API routes
    path('api/', include(router.urls)),
]