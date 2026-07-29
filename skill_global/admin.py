from django.contrib import admin
from .models import About, Course, LiveClass, Article

# Register your models here.

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'created_at', 'updated_at')
    search_fields = ('title', 'subtitle', 'description', 'mission', 'vision')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'author', 'summary', 'content')
    readonly_fields = ('published_at',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'level', 'is_active', 'created_at')
    list_filter = ('category', 'level', 'is_active')
    search_fields = ('title', 'category', 'instructor', 'short_description', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'instructor',
        'topic',
        'scheduled_at',
        'duration',
        'is_active',
    )

    list_filter = (
        'is_active',
        'scheduled_at',
    )

    search_fields = (
        'title',
        'instructor',
        'topic',
        'description',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = ('scheduled_at',)
