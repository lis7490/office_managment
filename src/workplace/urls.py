from django.urls import path
from . import views

urlpatterns = [
    path('response/', views.response),
    path('redir/', views.redir),
    path('red/', views.red),
    path('make/', views.render_html),
    path('render/', views.render_template)
    
]