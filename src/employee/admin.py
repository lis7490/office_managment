from django.contrib import admin
from django.utils.html import format_html
from .models import Employee, Skill, Desk, EmployeeSkill, EmployeeImage, Reservation

class EmployeeImageInline(admin.TabularInline):
    model = EmployeeImage
    extra = 1
    readonly_fields = ['preview_image']
    
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"
    preview_image.short_description = 'Предпросмотр'

class EmployeeSkillInline(admin.TabularInline):
    model = EmployeeSkill
    extra = 1

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'position', 'desk_number', 'hire_date', 'gender', 'main_photo_preview']
    list_filter = ['position', 'gender', 'skills']
    search_fields = ['last_name', 'first_name', 'email']
    inlines = [EmployeeSkillInline, EmployeeImageInline]
    
    def main_photo_preview(self, obj):
        main_photo = obj.get_main_photo()
        if main_photo and main_photo.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', main_photo.image.url)
        return "📷"
    main_photo_preview.short_description = 'Фото'

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Desk)
class DeskAdmin(admin.ModelAdmin):
    list_display = ['number', 'location', 'coordinates_x', 'coordinates_y', 'is_available']
    list_filter = ['is_available']
    search_fields = ['number', 'location']

@admin.register(EmployeeSkill)
class EmployeeSkillAdmin(admin.ModelAdmin):
    list_display = ['employee', 'skill', 'level']
    list_filter = ['level', 'skill']
    search_fields = ['employee__first_name', 'employee__last_name', 'skill__name']

@admin.register(EmployeeImage)
class EmployeeImageAdmin(admin.ModelAdmin):
    list_display = ['employee', 'preview_image', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['employee__first_name', 'employee__last_name']
    readonly_fields = ['preview_image']
    
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="200" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"
    preview_image.short_description = 'Предпросмотр'

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'desk', 'date', 'created_at']
    list_filter = ['date', 'desk']
    search_fields = ['user__username', 'desk__number']