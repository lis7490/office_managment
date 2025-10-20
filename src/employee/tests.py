from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Employee, Desk, Reservation, Skill

User = get_user_model()

# 1. Тесты для модели Employee
class EmployeeModelTest(TestCase):
    
    def setUp(self):
        self.employee = Employee.objects.create(
            first_name="Иван",
            last_name="Петров",
            position="backend",
            desk_number=1
        )
    
    def test_employee_creation(self):
        """Тест создания сотрудника"""
        self.assertEqual(self.employee.first_name, "Иван")
        self.assertEqual(self.employee.last_name, "Петров")
        self.assertEqual(self.employee.position, "backend")
        self.assertEqual(self.employee.desk_number, 1)
    
    def test_employee_string_representation(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.employee), "Иван Петров")
    
    def test_employee_default_values(self):
        """Тест значений по умолчанию"""
        employee = Employee.objects.create(
            first_name="Тест",
            last_name="Тестов"
            # position будет использовать значение по умолчанию 'backend'
        )
        self.assertEqual(employee.position, "backend")
        self.assertEqual(employee.desk_number, 1)
        self.assertEqual(employee.first_name, "Тест")
        self.assertEqual(employee.last_name, "Тестов")
    
    def test_employee_all_positions(self):
        """Тест создания сотрудников со всеми допустимыми должностями"""
        positions = ['backend', 'frontend', 'tester', 'manager', 'designer']
        
        # Используем разные номера столов, которые не являются соседними
        desk_numbers = [1, 10, 20, 30, 40]  # Столы далеко друг от друга
        
        for i, (position, desk_number) in enumerate(zip(positions, desk_numbers), 1):
            employee = Employee.objects.create(
                first_name=f"Сотрудник{i}",
                last_name="Тестов",
                position=position,
                desk_number=desk_number
            )
            self.assertEqual(employee.position, position)

# 2. Тесты для модели Desk
class DeskModelTest(TestCase):
    
    def setUp(self):
        self.desk = Desk.objects.create(
            number="A1",
            location="First Floor",
            coordinates_x=0,
            coordinates_y=0
        )
    
    def test_desk_creation(self):
        """Тест создания стола"""
        self.assertEqual(self.desk.number, "A1")
        self.assertEqual(self.desk.location, "First Floor")
        self.assertEqual(self.desk.coordinates_x, 0)
        self.assertEqual(self.desk.coordinates_y, 0)
        self.assertTrue(self.desk.is_available)
    
    def test_desk_string_representation(self):
        """Тест строкового представления стола"""
        self.assertEqual(str(self.desk), "Desk A1")
    
    def test_desk_with_default_coordinates(self):
        """Тест создания стола с координатами по умолчанию"""
        desk = Desk.objects.create(number="B1")
        self.assertEqual(desk.coordinates_x, 0)
        self.assertEqual(desk.coordinates_y, 0)

# 3. Тесты для модели Reservation
class ReservationModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        self.desk = Desk.objects.create(
            number="B1",
            coordinates_x=1,
            coordinates_y=1
        )
    
    def test_reservation_creation(self):
        """Тест создания резервации"""
        reservation = Reservation.objects.create(
            user=self.user,
            desk=self.desk,
            date="2024-01-15"
        )
        self.assertEqual(reservation.user.username, "testuser")
        self.assertEqual(reservation.desk.number, "B1")
        self.assertEqual(str(reservation.date), "2024-01-15")
    
    def test_unique_reservation_constraint(self):
        """Тест ограничения уникальности резервации"""
        Reservation.objects.create(
            user=self.user,
            desk=self.desk,
            date="2024-01-15"
        )
        
        # Попытка создать дублирующую резервацию
        with self.assertRaises(ValidationError):
            reservation2 = Reservation(
                user=self.user,
                desk=self.desk, 
                date="2024-01-15"
            )
            reservation2.full_clean()

# 4. Тесты для URL
class URLTest(TestCase):
    
    def setUp(self):
        self.client = Client()
    
    def test_admin_url(self):
        """Тест доступности админки"""
        response = self.client.get('/admin/')
        self.assertIn(response.status_code, [200, 302])
    
    def test_home_url(self):
        """Тест доступности главной страницы"""
        response = self.client.get('/')
        self.assertIn(response.status_code, [200, 302, 404])

# 5. Тесты для валидации разработчиков и тестировщиков
class DeveloperTesterValidationTest(TestCase):
    
    def test_developer_tester_non_adjacent_desks(self):
        """Тест: разработчик и тестировщик на НЕсоседних столах - должно работать"""
        # Создаем разработчика на столе 1
        developer = Employee.objects.create(
            first_name="Разработчик",
            last_name="Программистов",
            position="backend",
            desk_number=1
        )
        
        # Создаем тестировщика на столе 10 (не соседний)
        tester = Employee.objects.create(
            first_name="Тестировщик",
            last_name="Тестов",
            position="tester", 
            desk_number=10
        )
        
        # Это должно работать без ошибок
        try:
            developer.full_clean()
            tester.full_clean()
        except ValidationError:
            self.fail("ValidationError raised for non-adjacent desks")
    
    def test_developer_tester_adjacent_desks_validation(self):
        """Тест валидации разработчика и тестировщика на соседних столах"""
        # Создаем разработчика на столе 1
        developer = Employee.objects.create(
            first_name="Разработчик",
            last_name="Кодов",
            position="backend",
            desk_number=1
        )
        
        # Пытаемся создать тестировщика на соседнем столе 2
        tester = Employee(
            first_name="Тестировщик",
            last_name="Багова",
            position="tester",
            desk_number=2  # Соседний стол
        )
        
        # Должна возникнуть ошибка валидации
        with self.assertRaises(ValidationError) as context:
            tester.full_clean()
        
        self.assertIn('Тестировщики и разработчики не могут работать за соседними столами', str(context.exception))
    
    def test_same_role_adjacent_desks_allowed(self):
        """Тест что два разработчика могут сидеть на соседних столах"""
        # Создаем первого разработчика на столе 1
        developer1 = Employee.objects.create(
            first_name="Разработчик1",
            last_name="Первый",
            position="backend",
            desk_number=1
        )
        
        # Создаем второго разработчика на соседнем столе 2
        developer2 = Employee.objects.create(
            first_name="Разработчик2",
            last_name="Второй",
            position="frontend",
            desk_number=2  # Соседний стол
        )
        
        # Это должно работать без ошибок (оба разработчики)
        try:
            developer1.full_clean()
            developer2.full_clean()
        except ValidationError:
            self.fail("ValidationError raised for same-role adjacent desks")

# 6. Тесты для Skills
class SkillModelTest(TestCase):
    
    def setUp(self):
        self.skill = Skill.objects.create(name="Python")
    
    def test_skill_creation(self):
        """Тест создания навыка"""
        self.assertEqual(self.skill.name, "Python")
    
    def test_skill_string_representation(self):
        """Тест строкового представления навыка"""
        self.assertEqual(str(self.skill), "Python")

# 7. Базовые тесты
class BasicTest(TestCase):
    """Простые тесты для проверки окружения"""
    
    def test_basic_assertions(self):
        """Тест базовых утверждений"""
        self.assertEqual(1 + 1, 2)
        self.assertTrue(1 < 2)
        self.assertFalse(1 > 2)
    
    def test_database_operations(self):
        """Тест операций с базой данных"""
        desk = Desk.objects.create(
            number="TEST1",
            coordinates_x=5,
            coordinates_y=5
        )
        
        desk_from_db = Desk.objects.get(number="TEST1")
        self.assertEqual(desk.number, desk_from_db.number)
        
        desk_count_before = Desk.objects.count()
        desk.delete()
        desk_count_after = Desk.objects.count()
        self.assertEqual(desk_count_after, desk_count_before - 1)

# 8. Тесты для Employee-Desk взаимодействия
class EmployeeDeskInteractionTest(TestCase):
    
    def test_multiple_employees_different_desks(self):
        """Тест создания нескольких сотрудников на разных столах"""
        employee1 = Employee.objects.create(
            first_name="Анна",
            last_name="Иванова",
            position="frontend",
            desk_number=1
        )
        
        employee2 = Employee.objects.create(
            first_name="Петр",
            last_name="Сидоров", 
            position="manager",
            desk_number=10  # Далекий стол
        )
        
        self.assertEqual(employee1.desk_number, 1)
        self.assertEqual(employee2.desk_number, 10)
        self.assertNotEqual(employee1.desk_number, employee2.desk_number)
    
    def test_employee_position_choices(self):
        """Тест что все позиции из CHOICES работают корректно"""
        test_cases = [
            ('backend', 'Бекенд-разработчик'),
            ('frontend', 'Фронтенд-разработчик'),
            ('tester', 'Тестировщик'),
            ('manager', 'Менеджер'),
            ('designer', 'Дизайнер'),
        ]
        
        # Используем разные номера столов чтобы избежать конфликтов валидации
        desk_number = 100
        
        for position_code, position_name in test_cases:
            with self.subTest(position=position_code):
                employee = Employee.objects.create(
                    first_name="Тест",
                    last_name="Тестов",
                    position=position_code,
                    desk_number=desk_number
                )
                self.assertEqual(employee.get_position_display(), position_name)
                desk_number += 10  # Увеличиваем номер стола для следующего теста

# 9. Тесты для граничных случаев
class EdgeCaseTests(TestCase):
    
    def test_employees_with_same_desk_number(self):
        """Тест что несколько сотрудников могут иметь одинаковый номер стола"""
        # Это возможно, если валидация это позволяет
        employee1 = Employee.objects.create(
            first_name="Сотрудник1",
            last_name="Один",
            position="manager",
            desk_number=5
        )
        
        employee2 = Employee.objects.create(
            first_name="Сотрудник2",
            last_name="Два",
            position="designer",
            desk_number=5  # Тот же номер стола
        )
        
        self.assertEqual(employee1.desk_number, employee2.desk_number)
    
    def test_developer_tester_far_apart(self):
        """Тест что разработчик и тестировщик на далеких столах работают нормально"""
        developer = Employee.objects.create(
            first_name="Разработчик",
            last_name="Дальний",
            position="backend",
            desk_number=1
        )
        
        tester = Employee.objects.create(
            first_name="Тестировщик",
            last_name="Далекий",
            position="tester",
            desk_number=100  # Очень далекий стол
        )
        
        # Не должно быть ошибок валидации
        try:
            developer.full_clean()
            tester.full_clean()
        except ValidationError:
            self.fail("ValidationError raised for far apart desks")