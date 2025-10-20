from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from employee.models import Employee

class Command(BaseCommand):
    help = 'Настройка прав доступа для приложения employee'

    def handle(self, *args, **options):
        try:
            content_type = ContentType.objects.get_for_model(Employee)
            
            # Создаем или получаем разрешение
            move_permission, created = Permission.objects.get_or_create(
                codename='can_move_employees',
                name='Может перемещать сотрудников между столами',
                content_type=content_type,
            )
            
            # Создаем или получаем группу "Смотритель"
            keeper_group, created = Group.objects.get_or_create(name='Смотритель')
            keeper_group.permissions.add(move_permission)
            
            self.stdout.write(
                self.style.SUCCESS('Права доступа успешно настроены')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Создана группа "Смотритель" с правом: {move_permission.name}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при настройке прав доступа: {e}')
            )