import math

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Profile, LiveClass, Article, Course, About, Testimonial, CourseEnrollment
from django.shortcuts import get_object_or_404
import razorpay
from django.conf import settings
from django.http import JsonResponse

User = get_user_model()

# Create your views here.

def index(request):
    featured_courses = Course.objects.filter(is_active=True).order_by('title')[:4]
    about = About.objects.first()
    live_classes = LiveClass.objects.filter(
        is_active=True,
        status__in=(LiveClass.STATUS_LIVE, LiveClass.STATUS_UPCOMING)
    ).order_by('scheduled_at')[:2]
    latest_articles = list(Article.objects.filter(is_published=True).order_by('-published_at')[:3])
    for article in latest_articles:
        word_count = len(article.content.split()) if article.content else 0
        article.reading_time = max(1, math.ceil(word_count / 200))
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-id')[:3]
    context = {
        'page_title': 'Home',
        'page_description': 'Skill Global offers premium training, live mentoring, and certification pathways for students and professionals ready to accelerate their career.',
        'featured_courses': featured_courses,
        'about': about,
        'live_classes': live_classes,
        'latest_articles': latest_articles,
        'testimonials': testimonials,
    }
    return render(request, 'skill_global/index.html', context)


def testimonials(request):
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-id')
    context = {
        'page_title': 'Testimonials',
        'page_description': 'Read what learners are saying about Skill Global training and support.',
        'testimonials': testimonials,
    }
    return render(request, 'skill_global/testimonials.html', context)


from django.db.models import Q

def courses(request):
    query = request.GET.get('q', '')

    courses = Course.objects.filter(is_active=True)

    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(category__icontains=query) |
            Q(instructor__icontains=query)
        )

    context = {
        'page_title': 'Courses',
        'page_description': 'Browse premium courses designed to help you build career-ready skills.',
        'courses': courses,
        'query': query,
    }

    return render(request, 'skill_global/courses.html', context)

def course_detail(request, id):
    course = get_object_or_404(Course, id=id, is_active=True)
    
    # Fetch related courses from the same category, excluding current course, limit to 3
    related_courses = Course.objects.filter(
        category=course.category,
        is_active=True
    ).exclude(id=course.id)[:3]
    
    context = {
        'page_title': course.title,
        'page_description': 'View detailed information about this course.',
        'course': course,
        'related_courses': related_courses,
    }
    return render(request, 'skill_global/course_detail.html', context)


def course_enroll(request, slug):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")

    course = get_object_or_404(
        Course,
        slug=slug,
        is_active=True
    )

    enrollment, created = CourseEnrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            'amount': course.price or 0,
            'payment_status': 'Pending',
            'order_status': 'Pending',
        }
    )

    # Already paid enrollment
    if (
        enrollment.payment_status == 'Paid'
        and enrollment.order_status == 'Confirmed'
    ):
        return redirect(
            'enrollment_success',
            enrollment_id=enrollment.enrollment_id
        )

    user_phone = (
        request.user.phone
        or getattr(
            getattr(request.user, 'profile', None),
            'phone',
            ''
        )
    )

    # =========================
    # POST - START PAYMENT
    # =========================
    if request.method == 'POST':

        payment_method = request.POST.get(
            'payment_method',
            'UPI'
        )
        phone = request.POST.get('phone', user_phone)

        agree_terms = request.POST.get('agree_terms') == 'on'

        # Terms validation
        if not agree_terms:
            context = {
                'page_title': 'Course Enrollment',
                'page_description': 'Complete your enrollment securely.',
                'course': course,
                'enrollment': enrollment,
                'user_full_name': (
                    request.user.get_full_name()
                    or request.user.email
                ),
                'user_email': request.user.email,
                'user_phone': user_phone,
                'error': (
                    'You must agree to the Terms & Conditions '
                    'and Refund Policy to continue.'
                ),
            }

            return render(
                request,
                'skill_global/course_enrollment.html',
                context
            )

        # Phone validation
        if not phone:
            context = {
                'page_title': 'Course Enrollment',
                'page_description': 'Complete your enrollment securely.',
                'course': course,
                'enrollment': enrollment,
                'user_full_name': (
                    request.user.get_full_name()
                    or request.user.email
                ),
                'user_email': request.user.email,
                'user_phone': user_phone,
                'error': 'Please enter a valid phone number.',
            }

            return render(
                request,
                'skill_global/course_enrollment.html',
                context
            )

        # Extract additional user details from modal
        branch = request.POST.get('detail_branch', '')
        specialization = request.POST.get('detail_specialization', '')
        dob_str = request.POST.get('detail_dob', '')
        address = request.POST.get('detail_address', '')
        
        # Parse date of birth
        date_of_birth = None
        if dob_str:
            try:
                from datetime import datetime
                date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except:
                pass

        # =========================
        # FREE COURSE
        # =========================
        if not course.price or course.price <= 0:

            enrollment.payment_method = payment_method
            enrollment.amount = 0
            enrollment.payment_status = 'Paid'
            enrollment.order_status = 'Confirmed'
            enrollment.branch = branch
            enrollment.specialization = specialization
            enrollment.date_of_birth = date_of_birth
            enrollment.address = address
            enrollment.save()

            return redirect(
                'enrollment_success',
                enrollment_id=enrollment.enrollment_id
            )

        # =========================
        # PAID COURSE - RAZORPAY
        # =========================

        enrollment.payment_method = payment_method
        enrollment.amount = course.price
        enrollment.payment_status = 'Pending'
        enrollment.order_status = 'Pending'
        enrollment.branch = branch
        enrollment.specialization = specialization
        enrollment.date_of_birth = date_of_birth
        enrollment.address = address
        enrollment.save()

        # Razorpay client
        try:
            client = razorpay.Client(
                auth=(
                    settings.RAZORPAY_KEY_ID,
                    settings.RAZORPAY_KEY_SECRET
                )
            )

            amount_paise = int(enrollment.amount * 100)

            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': enrollment.enrollment_id,
                'payment_capture': 1,
            })

            enrollment.razorpay_order_id = razorpay_order['id']
            enrollment.save()

            context = {
                'page_title': 'Course Enrollment',
                'page_description': 'Complete your enrollment securely.',
                'course': course,
                'enrollment': enrollment,
                'user_full_name': (
                    request.user.get_full_name()
                    or request.user.email
                ),
                'user_email': request.user.email,
                'user_phone': phone,

                # Razorpay data
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_amount': amount_paise,
                'razorpay_currency': 'INR',
                'open_razorpay': True,
            }

            return render(
                request,
                'skill_global/course_enrollment.html',
                context
            )

        except Exception as e:
            enrollment.payment_status = 'Failed'
            enrollment.order_status = 'Cancelled'
            enrollment.save()

            context = {
                'page_title': 'Course Enrollment',
                'page_description': 'Complete your enrollment securely.',
                'course': course,
                'enrollment': enrollment,
                'user_full_name': (
                    request.user.get_full_name()
                    or request.user.email
                ),
                'user_email': request.user.email,
                'user_phone': user_phone,
                'error': 'Unable to process payment. Please try again later.',
            }

            return render(
                request,
                'skill_global/course_enrollment.html',
                context
            )

    # =========================
    # GET - SHOW ENROLLMENT PAGE
    # =========================

    context = {
        'page_title': 'Course Enrollment',
        'page_description': 'Complete your enrollment securely.',
        'course': course,
        'enrollment': enrollment,
        'user_full_name': (
            request.user.get_full_name()
            or request.user.email
        ),
        'user_email': request.user.email,
        'user_phone': user_phone,
    }

    return render(
        request,
        'skill_global/course_enrollment.html',
        context
    )

def enrollment_success(request, enrollment_id):
    enrollment = get_object_or_404(CourseEnrollment, enrollment_id=enrollment_id, user=request.user)
    if enrollment.payment_status != 'Paid' or enrollment.order_status != 'Confirmed':
        return redirect('course_enrollment', slug=enrollment.course.slug)

    context = {
        'page_title': 'Enrollment Successful',
        'page_description': 'Your course enrollment is confirmed.',
        'enrollment': enrollment,
    }
    return render(request, 'skill_global/enrollment_success.html', context)


def payment_failed(request):
    context = {
        'page_title': 'Payment Failed',
        'page_description': 'Your payment could not be completed.',
    }
    return render(request, 'skill_global/payment_failed.html', context)
def razorpay_verify(request):
    """Verify Razorpay payment signature and confirm enrollment"""
    
    # Get payment details from request
    payment_id = request.GET.get('razorpay_payment_id')
    order_id = request.GET.get('razorpay_order_id')
    signature = request.GET.get('razorpay_signature')

    # Validate required fields
    if not all([payment_id, order_id, signature]):
        return redirect('payment_failed')

    try:
        # Get enrollment record
        enrollment = get_object_or_404(
            CourseEnrollment,
            razorpay_order_id=order_id,
            user=request.user
        )

        # Initialize Razorpay client
        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        # Verify payment signature
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        # Update enrollment with payment details
        enrollment.razorpay_payment_id = payment_id
        enrollment.razorpay_signature = signature
        enrollment.payment_status = 'Paid'
        enrollment.order_status = 'Confirmed'
        enrollment.save()

        # Redirect to success page
        return redirect(
            'enrollment_success',
            enrollment_id=enrollment.enrollment_id
        )

    except Exception as e:
        # Handle payment verification failure
        try:
            enrollment.payment_status = 'Failed'
            enrollment.order_status = 'Cancelled'
            enrollment.save()
        except:
            pass
        
        return redirect('payment_failed')


def my_courses(request):
    if not request.user.is_authenticated:
        return redirect('login')

    enrollments = CourseEnrollment.objects.filter(
        user=request.user,
        payment_status='Paid',
        order_status='Confirmed',
    ).select_related('course').order_by('-created_at')

    context = {
        'page_title': 'My Courses',
        'page_description': 'View the courses you are enrolled in.',
        'enrollments': enrollments,
    }
    return render(request, 'skill_global/my_courses.html', context)


def live_classes(request):
    live_classes = LiveClass.objects.filter(is_active=True).order_by('scheduled_at')
    context = {
        'page_title': 'Live Classes',
        'page_description': 'Join live sessions led by experts and sharpen your skills in real time.',
        'live_classes': live_classes,
    }
    return render(request, 'skill_global/live_classes.html', context)


def articles(request):
    articles = Article.objects.filter(is_published=True).order_by('-published_at')
    context = {
        'page_title': 'Articles',
        'page_description': 'Read expert-written articles on career growth, industry skills, and learning best practices.',
        'articles': articles,
    }
    return render(request, 'skill_global/articles.html', context)
def article_detail(request, slug):
    article = get_object_or_404(
        Article,
        slug=slug,
        is_published=True
    )

    related_articles = Article.objects.filter(
        is_published=True
    ).exclude(
        id=article.id
    ).order_by('-published_at')[:3]

    context = {
        'page_title': article.title,
        'page_description': article.summary,
        'article': article,
        'related_articles': related_articles,
    }

    return render(
        request,
        'skill_global/article_detail.html',
        context
    )


def contact(request):
    context = {
        'page_title': 'Contact',
        'page_description': 'Get in touch with Skill Global for questions about courses, partnerships, and learning support.',
    }
    return render(request, 'skill_global/contact.html', context)


def register(request):
    context = {
        'page_title': 'Register',
        'page_description': 'Create your account and start your learning journey with Skill Global.'
    }
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()

        if not full_name or not email or not password:
            context['error'] = 'Please fill in all fields.'
        elif User.objects.filter(email=email).exists():
            context['error'] = 'A user with that email already exists.'
        else:
            # create user via custom manager using email as identifier
            parts = full_name.split()
            first_name = parts[0] if parts else ''
            last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                phone=phone,
                message='',
            )
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = phone
            profile.save()
            auth_login(request, user)
            return redirect('profile')

    return render(request, 'skill_global/register.html', context)


def profile(request):
    user = request.user
    profile = None
    if user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=user)

    context = {
        'page_title': 'Profile',
        'page_description': 'View your account details and learning progress.',
        'user': user,
        'profile': profile,
        'stats': {
            'courses': Course.objects.filter(is_active=True).count(),
            'certificates': 5,
            'live_classes': LiveClass.objects.filter(is_active=True).count(),
            'articles': Article.objects.filter(is_published=True).count(),
        },
    }
    return render(request, 'skill_global/profile.html', context)


@ensure_csrf_cookie
def sign_in(request):
    if request.user.is_authenticated:
        return redirect('profile')

    context = {
        'page_title': 'Sign In',
        'page_description': 'Sign in to access your Skill Global account.'
    }

    next_url = request.GET.get('next') or request.POST.get('next')
    context['next'] = next_url

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()

        # authenticate using the model's USERNAME_FIELD (email)
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Successfully signed in.')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('profile')

        context['error'] = 'Invalid email or password.'

    return render(request, 'skill_global/login.html', context)


def sign_out(request):
    auth_logout(request)
    messages.success(request, 'You have been signed out.')
    return redirect('home')


def edit_profile(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('profile')

    profile, _ = Profile.objects.get_or_create(user=user)
    errors = []

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        bio = request.POST.get('bio', '').strip()
        profile_image = request.FILES.get('profile_image')
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not full_name:
            errors.append('Full Name is required.')
        if not email:
            errors.append('Email is required.')
        elif User.objects.filter(email=email).exclude(pk=user.pk).exists():
            errors.append('Email is already in use.')

        if new_password or confirm_password:
            if new_password != confirm_password:
                errors.append('The new passwords do not match.')
            elif len(new_password) < 8:
                errors.append('Password must be at least 8 characters long.')

        if not errors:
            parts = full_name.split()
            user.first_name = parts[0] if parts else ''
            user.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
            user.full_name = full_name
            user.email = email
            if new_password and hasattr(user, 'set_password'):
                user.set_password(new_password)
            user.save()

            profile.phone = phone
            profile.bio = bio
            if profile_image:
                profile.image = profile_image
            profile.save()

            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')

    context = {
        'page_title': 'Edit Profile',
        'page_description': 'Update your profile details.',
        'user': user,
        'profile': profile,
        'errors': errors,
    }
    return render(request, 'skill_global/edit_profile.html', context)


def about(request):
    about = About.objects.first()
    context = {
        'page_title': 'About Skill Global',
        'page_description': 'Empowering learners with practical skills, knowledge, and confidence for a changing world.',
        'about': about,
    }
    return render(request, 'skill_global/about.html', context)
