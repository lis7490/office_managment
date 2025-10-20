from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Employee, Skill, Desk, EmployeeSkill, EmployeeImage, Reservation

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']

class EmployeeSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    
    class Meta:
        model = EmployeeSkill
        fields = ['id', 'skill', 'skill_name', 'level']

class EmployeeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeImage
        fields = ['id', 'image', 'uploaded_at']

class DeskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Desk
        fields = ['id', 'number', 'location', 'coordinates_x', 'coordinates_y', 'is_available']

class EmployeeListSerializer(serializers.ModelSerializer):
    skills = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    work_experience_days = serializers.SerializerMethodField()
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'position', 'position_display',
            'desk_number', 'hire_date', 'gender', 'skills', 'work_experience_days'
        ]
    
    def get_work_experience_days(self, obj):
        return obj.get_work_experience_days()

class EmployeeDetailSerializer(serializers.ModelSerializer):
    skills_details = EmployeeSkillSerializer(source='employeeskill_set', many=True, read_only=True)
    images = EmployeeImageSerializer(many=True, read_only=True)
    work_experience_days = serializers.SerializerMethodField()
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'position', 'position_display',
            'desk_number', 'hire_date', 'gender', 'gender_display',
            'skills_details', 'images', 'work_experience_days'
        ]
    
    def get_work_experience_days(self, obj):
        return obj.get_work_experience_days()

class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    skills_data = EmployeeSkillSerializer(source='employeeskill_set', many=True, required=False)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'position', 'desk_number',
            'hire_date', 'gender', 'skills_data'
        ]
    
    def create(self, validated_data):
        skills_data = validated_data.pop('employeeskill_set', [])
        employee = Employee.objects.create(**validated_data)
        for skill_data in skills_data:
            EmployeeSkill.objects.create(employee=employee, **skill_data)
        return employee
    
    def update(self, instance, validated_data):
        skills_data = validated_data.pop('employeeskill_set', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if skills_data is not None:
            instance.employeeskill_set.all().delete()
            for skill_data in skills_data:
                EmployeeSkill.objects.create(employee=instance, **skill_data)
        return instance

class EmployeeMoveSerializer(serializers.Serializer):
    desk_number = serializers.IntegerField(min_value=1)
    
    def validate_desk_number(self, value):
        if not Desk.objects.filter(number=value).exists():
            raise serializers.ValidationError("Стол с таким номером не существует")
        return value

class ReservationSerializer(serializers.ModelSerializer):
    desk_number = serializers.CharField(source='desk.number', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Reservation
        fields = ['id', 'user', 'user_name', 'desk', 'desk_number', 'date', 'created_at']
        read_only_fields = ['user', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user