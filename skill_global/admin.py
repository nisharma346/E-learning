from django.contrib import admin
from .models import CustomUser, About, Course

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'created_at', 'updated_at')
    search_fields = ('title', 'subtitle', 'description', 'mission', 'vision')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'level', 'is_active', 'created_at')
    list_filter = ('category', 'level', 'is_active')
    search_fields = ('title', 'category', 'instructor', 'short_description', 'description')
    readonly_fields = ('created_at', 'updated_at')
