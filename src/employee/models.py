from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Desk(models.Model):
    number = models.CharField(max_length=10, unique=True)
    location = models.CharField(max_length=100, blank=True)
    coordinates_x = models.IntegerField(default=0)
    coordinates_y = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Desk {self.number}"

class Skill(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название навыка')
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    POSITION_CHOICES = [
        ('backend', 'Бекенд-разработчик'),
        ('frontend', 'Фронтенд-разработчик'), 
        ('tester', 'Тестировщик'),
        ('manager', 'Менеджер'),
        ('designer', 'Дизайнер'),
    ]
    
    GENDER_CHOICES = [  # ДОБАВЛЕНО
        ('male', 'Мужской'),
        ('female', 'Женский'),
    ]
    
    first_name = models.CharField(max_length=100, verbose_name='Имя', default="Unknown")
    last_name = models.CharField(max_length=100, verbose_name='Фамилия', default="Employee")
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, verbose_name='Должность', default='backend')
    desk_number = models.IntegerField(verbose_name='Номер стола', default=1)
    hire_date = models.DateField(default=timezone.now, verbose_name='Дата приёма на работу')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='Пол', default='male')
    skills = models.ManyToManyField('Skill', through='EmployeeSkill', verbose_name='Навыки')
    
    def clean(self):
        super().clean()
        self.validate_developer_tester_separation()
    
    def validate_developer_tester_separation(self):
        """Валидатор, который не допускает нахождение тестировщиков и разработчиков за соседними столами"""
        if self.position in ['backend', 'frontend', 'tester']:
            # Проверяем соседние столы
            adjacent_desks = [self.desk_number - 1, self.desk_number + 1]
            
            # Получаем сотрудников на соседних столах
            adjacent_employees = Employee.objects.filter(
                desk_number__in=adjacent_desks
            ).exclude(pk=self.pk if self.pk else None)
            
            for employee in adjacent_employees:
                if (self.position == 'tester' and employee.position in ['backend', 'frontend']) or \
                   (self.position in ['backend', 'frontend'] and employee.position == 'tester'):
                    raise ValidationError(
                        f'Тестировщики и разработчики не могут работать за соседними столами. '
                        f'Стол {self.desk_number} соседствует со столом {employee.desk_number}, '
                        f'где работает {employee.get_position_display()} {employee.first_name} {employee.last_name}'
                    )
    
    def save(self, *args, **kwargs):
        # Выполняем полную валидацию при сохранении
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_work_experience_days(self):
        """Рассчитывает стаж работы в днях"""
        return (timezone.now().date() - self.hire_date).days
    
    def get_main_photo(self):
        """Возвращает первое изображение из галереи"""
        return self.images.first()
    
    def get_gallery_photos(self):
        """Возвращает все изображения кроме первого"""
        return self.images.all()[1:]
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class EmployeeSkill(models.Model):
    LEVEL_CHOICES = [
        (1, 'Начальный'),
        (2, 'Средний'),
        (3, 'Продвинутый'),
        (4, 'Эксперт'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.IntegerField(choices=LEVEL_CHOICES, verbose_name='Уровень освоения')
    
    def __str__(self):
        return f'{self.employee} - {self.skill} ({self.get_level_display()})'

class EmployeeImage(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='employees/', verbose_name='Изображение')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f'Изображение {self.employee}'

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    desk = models.ForeignKey(Desk, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['desk', 'date']
        
    def __str__(self):
        return f"{self.user.username} - {self.desk.number} - {self.date}"