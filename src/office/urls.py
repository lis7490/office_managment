from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from employee import views

from django.contrib import admin
from django.urls import path, include
from employee import views

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    
    # Страницы сотрудников
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    
    # API
    #path('api/', include('employee.urls')),
    
    # Админка
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)