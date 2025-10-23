from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from .models import Employee, Desk, Skill, EmployeeSkill, EmployeeImage, Reservation
from .serializers import (
    EmployeeListSerializer,
    EmployeeDetailSerializer,
    EmployeeCreateUpdateSerializer,
    EmployeeMoveSerializer,
    DeskSerializer,
    SkillSerializer,
    EmployeeSkillSerializer,
    EmployeeImageSerializer,
    ReservationSerializer,
    UserSerializer,
    UserRegistrationSerializer
)

# Временно используем встроенные permissions
class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с сотрудниками.
    """
    queryset = Employee.objects.all().prefetch_related('skills', 'images')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateUpdateSerializer
        return EmployeeDetailSerializer

    @action(detail=True, methods=['get'])
    def skills(self, request, pk=None):
        """Получить навыки сотрудника"""
        employee = self.get_object()
        skills = EmployeeSkill.objects.filter(employee=employee)
        serializer = EmployeeSkillSerializer(skills, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        """Получить фотографии сотрудника"""
        employee = self.get_object()
        photos = employee.images.all()
        serializer = EmployeeImageSerializer(photos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def move_desk(self, request, pk=None):
        """Переместить сотрудника на другой стол"""
        employee = self.get_object()
        serializer = EmployeeMoveSerializer(data=request.data)
        
        if serializer.is_valid():
            desk_number = serializer.validated_data['desk_number']
            try:
                employee.desk_number = desk_number
                employee.save()
                return Response({'status': 'Сотрудник перемещен'})
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_position(self, request):
        """Сотрудники по должности"""
        position = request.query_params.get('position', None)
        if position:
            employees = Employee.objects.filter(position=position)
            serializer = EmployeeListSerializer(employees, many=True)
            return Response(serializer.data)
        return Response([])

class DeskViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рабочими столами"""
    queryset = Desk.objects.all()
    serializer_class = DeskSerializer
    permission_classes = [permissions.IsAuthenticated]

class SkillViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с навыками"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

class EmployeeSkillViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с навыками сотрудников"""
    queryset = EmployeeSkill.objects.all().select_related('employee', 'skill')
    serializer_class = EmployeeSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

class EmployeeImageViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с изображениями сотрудников"""
    queryset = EmployeeImage.objects.all().select_related('employee')
    serializer_class = EmployeeImageSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReservationViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с бронированиями"""
    queryset = Reservation.objects.all().select_related('user', 'desk')
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра пользователей"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получить текущего пользователя"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class UserRegistrationView(APIView):
    """Регистрация нового пользователя"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {'message': 'Пользователь успешно создан'}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)