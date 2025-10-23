from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Desk(models.Model):
    """Модель рабочего стола"""
    number = models.CharField(
        max_length=10, 
        unique=True,
        verbose_name=_('Номер стола'),
        help_text=_('Уникальный номер стола (например: A-101)')
    )
    location = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('Расположение'),
        help_text=_('Описание расположения стола в офисе')
    )
    coordinates_x = models.IntegerField(
        default=0,
        verbose_name=_('Координата X'),
        help_text=_('Координата X на плане офиса')
    )
    coordinates_y = models.IntegerField(
        default=0,
        verbose_name=_('Координата Y'),
        help_text=_('Координата Y на плане офиса')
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name=_('Доступен'),
        help_text=_('Доступен ли стол для бронирования')
    )
    
    class Meta:
        verbose_name = _('Рабочий стол')
        verbose_name_plural = _('Рабочие столы')
        ordering = ['number']
    
    def __str__(self):
        return f"Стол {self.number}"

class Skill(models.Model):
    """Модель навыков сотрудников"""
    name = models.CharField(
        max_length=100, 
        verbose_name=_('Название навыка'),
        help_text=_('Название профессионального навыка')
    )
    
    class Meta:
        verbose_name = _('Навык')
        verbose_name_plural = _('Навыки')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    """Модель сотрудника компании"""

    class PositionChoices(models.TextChoices):
        BACKEND = 'backend', 'Бекенд-разработчик'
        FRONTEND = 'frontend', 'Фронтенд-разработчик'
        TESTER = 'tester', 'Тестировщик'
        MANAGER = 'manager', 'Менеджер'
        DESIGNER = 'designer', 'Дизайнер'
        DEVOPS = 'devops', 'DevOps инженер'
        ANALYST = 'analyst', 'Аналитик'

    class GenderChoices(models.TextChoices):
        MALE = 'male', 'Мужской'
        FEMALE = 'female', 'Женский'
    
    first_name = models.CharField(
        max_length=100, 
        verbose_name=_('Имя'),
        help_text=_('Имя сотрудника')
    )
    last_name = models.CharField(
        max_length=100, 
        verbose_name=_('Фамилия'),
        help_text=_('Фамилия сотрудника')
    )
    position = models.CharField(
        max_length=20, 
        choices=PositionChoices.choices, 
        verbose_name='Должность',
        default=PositionChoices.BACKEND,
        help_text='Должность сотрудника в компании')
    
    desk = models.ForeignKey(
        Desk,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Рабочий стол'),
        help_text=_('Закрепленный рабочий стол')
    )
    hire_date = models.DateField(
        default=timezone.now, 
        verbose_name=_('Дата приёма на работу'),
        help_text=_('Дата начала работы в компании')
    )
    gender = models.CharField(
        max_length=10, 
        choices=GenderChoices.choices, 
        verbose_name=_('Пол'),
        default=GenderChoices.MALE,
        help_text='Пол сотрудника'
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_('Email'),
        help_text=_('Корпоративный email адрес')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Телефон'),
        help_text=_('Контактный телефон')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен'),
        help_text=_('Работает ли сотрудник в компании')
    )
    skills = models.ManyToManyField(
        'Skill', 
        through='EmployeeSkill',
        verbose_name=_('Навыки'),
        help_text=_('Профессиональные навыки сотрудника')
    )
    
    class Meta:
        verbose_name = _('Сотрудник')
        verbose_name_plural = _('Сотрудники')
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['position']),
            models.Index(fields=['hire_date']),
        ]
    
    def clean(self):
        """Валидация данных сотрудника"""
        super().clean()
        if self.desk:
            self.validate_developer_tester_separation()
    
    def validate_developer_tester_separation(self):
        """
        Валидатор, который не допускает нахождение тестировщиков 
        и разработчиков за соседними столами
        """
        if self.position in [self.PositionChoices.BACKEND, 
                           self.PositionChoices.FRONTEND, 
                           self.PositionChoices.TESTER]:
            
            # Получаем соседние столы по координатам
            adjacent_desks = Desk.objects.filter(
                models.Q(coordinates_x=self.desk.coordinates_x + 1, coordinates_y=self.desk.coordinates_y) |
                models.Q(coordinates_x=self.desk.coordinates_x - 1, coordinates_y=self.desk.coordinates_y) |
                models.Q(coordinates_x=self.desk.coordinates_x, coordinates_y=self.desk.coordinates_y + 1) |
                models.Q(coordinates_x=self.desk.coordinates_x, coordinates_y=self.desk.coordinates_y - 1)
            )
            
            # Получаем сотрудников на соседних столах
            adjacent_employees = Employee.objects.filter(
                desk__in=adjacent_desks,
                is_active=True
            ).exclude(pk=self.pk if self.pk else None)
            
            for employee in adjacent_employees:
                if (self.position == self.PositionChoices.TESTER and 
                    employee.position in [self.PositionChoices.BACKEND, self.PositionChoices.FRONTEND]) or \
                   (self.position in [self.PositionChoices.BACKEND, self.PositionChoices.FRONTEND] and 
                    employee.position == self.PositionChoices.TESTER):
                    raise ValidationError(
                        _('Тестировщики и разработчики не могут работать за соседними столами. '
                          'Стол %(current_desk)s соседствует со столом %(adjacent_desk)s, '
                          'где работает %(position)s %(name)s') % {
                              'current_desk': self.desk.number,
                              'adjacent_desk': employee.desk.number,
                              'position': employee.get_position_display(),
                              'name': employee.get_full_name()
                          }
                    )
    
    def save(self, *args, **kwargs):
        """Сохранение с валидацией"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        """Возвращает полное имя сотрудника"""
        return f'{self.first_name} {self.last_name}'
    
    def get_work_experience_days(self):
        """Рассчитывает стаж работы в днях"""
        return (timezone.now().date() - self.hire_date).days
    
    def get_work_experience_years(self):
        """Рассчитывает стаж работы в годах"""
        from datetime import date
        today = date.today()
        experience = today - self.hire_date
        return experience.days // 365
    
    def get_main_photo(self):
        """Возвращает первое изображение из галереи"""
        return self.images.first()
    
    def get_gallery_photos(self):
        """Возвращает все изображения кроме первого"""
        return self.images.all()[1:]
    
    @property
    def desk_number(self):
        """Свойство для обратной совместимости"""
        return self.desk.number if self.desk else None
    
    def __str__(self):
        return f'{self.last_name} {self.first_name} ({self.get_position_display()})'

class EmployeeSkill(models.Model):
    """Промежуточная модель для навыков сотрудника"""
    
    class LevelChoices(models.IntegerChoices):
        BEGINNER = 1, _('Начальный')
        INTERMEDIATE = 2, _('Средний')
        ADVANCED = 3, _('Продвинутый')
        EXPERT = 4, _('Эксперт')
    
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name='employee_skills'
    )
    skill = models.ForeignKey(
        Skill, 
        on_delete=models.CASCADE,
        verbose_name=_('Навык')
    )
    level = models.IntegerField(
        choices=LevelChoices.choices, 
        verbose_name=_('Уровень освоения'),
        help_text=_('Уровень владения навыком')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата добавления')
    )
    
    class Meta:
        verbose_name = _('Навык сотрудника')
        verbose_name_plural = _('Навыки сотрудников')
        unique_together = ['employee', 'skill']
        ordering = ['-level', 'skill__name']
    
    def __str__(self):
        return f'{self.employee} - {self.skill} ({self.get_level_display()})'

class EmployeeImage(models.Model):
    """Модель для изображений сотрудников"""
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name=_('Сотрудник')
    )
    image = models.ImageField(
        upload_to='employees/gallery/%Y/%m/%d/',
        verbose_name=_('Изображение'),
        help_text=_('Фотография сотрудника')
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Описание'),
        help_text=_('Описание изображения')
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name=_('Основное фото'),
        help_text=_('Использовать как основное фото')
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата загрузки')
    )
    
    class Meta:
        verbose_name = _('Изображение сотрудника')
        verbose_name_plural = _('Изображения сотрудников')
        ordering = ['-is_main', 'uploaded_at']
    
    def __str__(self):
        return f'Изображение {self.employee}'

class Reservation(models.Model):
    """Модель бронирования рабочих столов"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь')
    )
    desk = models.ForeignKey(
        Desk, 
        on_delete=models.CASCADE,
        verbose_name=_('Стол')
    )
    date = models.DateField(
        verbose_name=_('Дата бронирования')
    )
    start_time = models.TimeField(
        default='09:00',
        verbose_name=_('Время начала')
    )
    end_time = models.TimeField(
        default='18:00',
        verbose_name=_('Время окончания')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    
    class Meta:
        verbose_name = _('Бронирование')
        verbose_name_plural = _('Бронирования')
        unique_together = ['desk', 'date']
        ordering = ['-date', 'desk__number']
    
    def clean(self):
        """Валидация бронирования"""
        if self.date < timezone.now().date():
            raise ValidationError(_('Нельзя забронировать стол на прошедшую дату'))
        
        if self.end_time <= self.start_time:
            raise ValidationError(_('Время окончания должно быть позже времени начала'))
    
    def __str__(self):
        return f'{self.user.username} - {self.desk.number} - {self.date}'