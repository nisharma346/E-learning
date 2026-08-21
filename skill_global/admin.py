from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import About, Course, CourseEnrollment, LiveClass, Article, Profile, Testimonial, CustomUser, Coupon
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Register your models here.

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_purchase_amount', 'valid_to', 'active', 'used_count', 'max_uses')
    list_filter = ('discount_type', 'active', 'created_at')
    search_fields = ('code',)
    readonly_fields = ('used_count', 'created_at')

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'created_at', 'updated_at')
    search_fields = ('title', 'subtitle', 'description', 'mission', 'vision')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'author',
        'featured',
        'is_published',
        'published_at',
    )

    list_filter = (
        'category',
        'featured',
        'is_published',
    )

    search_fields = (
        'title',
        'category',
        'author',
        'summary',
        'content',
        'tags',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }

    readonly_fields = (
        'published_at',
    )

    fieldsets = (
        ('Article Information', {
            'fields': (
                'title',
                'slug',
                'category',
                'author',
                'summary',
                'content',
            )
        }),

        ('Media & Reading Information', {
            'fields': (
                'image',
                'read_time',
                'tags',
            )
        }),

        ('Publishing', {
            'fields': (
                'featured',
                'is_published',
                'published_at',
            )
        }),
    )

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'level', 'is_active', 'created_at')
    list_filter = ('category', 'level', 'is_active')
    search_fields = ('title', 'category', 'instructor', 'short_description', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'enrollment_id',
        'user',
        'course',
        'amount',
        'payment_method',
        'payment_status',
        'order_status',
        'created_at',
    )
    list_filter = ('payment_method', 'payment_status', 'order_status', 'created_at')
    search_fields = ('enrollment_id', 'user__email', 'user__full_name', 'course__title')
    readonly_fields = ('enrollment_id', 'created_at', 'updated_at')

@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'instructor',
        'status',
        'scheduled_at',
        'featured',
        'is_active',
        'price',
        'created_at',
    )
    list_filter = (
        'status',
        'category',
        'featured',
        'is_active',
        'meeting_platform',
        'level',
    )
    search_fields = (
        'title',
        'instructor',
        'topic',
        'description',
        'tags',
        'meeting_link',
        'meeting_id',
    )
    readonly_fields = (
        'thumbnail_preview',
        'created_at',
        'updated_at',
    )
    ordering = ('display_order', 'scheduled_at')
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'topic',
                'category',
                'status',
                'class_type',
                'level',
                'language',
                'tags',
                'featured',
                'is_active',
            )
        }),
        ('Schedule & Meeting Details', {
            'fields': (
                'scheduled_at',
                'registration_deadline',
                'duration',
                'meeting_platform',
                'meeting_link',
                'meeting_id',
                'meeting_password',
            )
        }),
        ('Pricing & Capacity', {
            'fields': (
                'price',
                'discount_price',
                'certificate_available',
                'recording_available',
                'max_students',
                'enrolled_students',
                'display_order',
            )
        }),
        ('Content & Media', {
            'fields': (
                'description',
                'prerequisites',
                'learning_outcomes',
                'banner_color',
                'thumbnail',
                'thumbnail_preview',
                'slug',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="max-width: 250px; max-height: 150px; object-fit: cover;"/>', obj.thumbnail.url)
        return 'No image uploaded'

    thumbnail_preview.short_description = 'Thumbnail Preview'


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
