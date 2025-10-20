from django.apps import AppConfig

class EmployeeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employee'
    
    def ready(self):
        # Пока ничего не делаем, чтобы избежать запросов к БД при инициализации
        pass