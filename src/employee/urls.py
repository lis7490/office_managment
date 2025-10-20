from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('employees', views.EmployeeViewSet, basename='employees')
router.register('skills', views.SkillViewSet, basename='skills')
router.register('desks', views.DeskViewSet, basename='desks')
router.register('images', views.EmployeeImageViewSet, basename='images')
router.register('reservations', views.ReservationViewSet, basename='reservations')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/me/', views.CurrentUserView.as_view(), name='current-user'),
]