from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import About, Course, LiveClass, Article, Profile, Testimonial, CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

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


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'designation', 'rating', 'verified', 'is_active', 'created_at')
    list_filter = ('is_active', 'verified')
    search_fields = ('student_name', 'designation', 'review')
    readonly_fields = ('created_at', 'updated_at')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'full_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('email',)
    search_fields = ('email', 'full_name')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'full_name', 'phone', 'bio', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )
    inlines = (ProfileInline,)
