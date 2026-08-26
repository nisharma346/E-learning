import math
import logging

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Profile, LiveClass, Article, Course, About, Testimonial, CourseEnrollment, Coupon
from django.shortcuts import get_object_or_404
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.core.mail import send_mail
from django.db import transaction

User = get_user_model()
logger = logging.getLogger(__name__)

def send_enrollment_confirmation_email(enrollment):
    """Sends confirmation email with invoice details to student upon successful enrollment."""
    try:
        if not enrollment or not enrollment.user or not enrollment.user.email:
            return
        subject = f"Enrollment Confirmed: {enrollment.course.title} | Skill Global"
        message = (
            f"Dear {enrollment.user.get_full_name() or enrollment.user.email},\n\n"
            f"Thank you for enrolling in '{enrollment.course.title}' at Skill Global!\n\n"
            f"--- ENROLLMENT DETAILS ---\n"
            f"Enrollment ID: {enrollment.enrollment_id}\n"
            f"Course: {enrollment.course.title}\n"
            f"Amount Paid: ₹{enrollment.amount}\n"
            f"Payment Status: {enrollment.payment_status}\n\n"
            f"You can view your course materials and download your official tax invoice anytime from your account dashboard.\n\n"
            f"Happy Learning!\n"
            f"Skill Global Team"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'Skill Global <noreply@skillglobal.com>'),
            recipient_list=[enrollment.user.email],
            fail_silently=True
        )
    except Exception as e:
        print("Email notification warning:", e)


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def apply_coupon(request):
    """AJAX endpoint to validate and calculate coupon discount for checkout"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

    code = request.POST.get('coupon_code', '').strip().upper()
    course_id = request.POST.get('course_id')

    if not code:
        return JsonResponse({'success': False, 'error': 'Please enter a promo code.'}, status=400)

    course = None
    if course_id:
        course = Course.objects.filter(id=course_id).first()

    original_amount = float(course.price) if (course and course.price) else 0.0

    coupon = Coupon.objects.filter(code=code).first()
    if not coupon:
        return JsonResponse({'success': False, 'error': 'Invalid promo code. Please check and try again.'}, status=404)

    is_valid, msg = coupon.is_valid(original_amount)
    if not is_valid:
        return JsonResponse({'success': False, 'error': msg}, status=400)

    discount_amount = coupon.calculate_discount(original_amount)
    final_amount = max(0.0, round(original_amount - discount_amount, 2))

    return JsonResponse({
        'success': True,
        'coupon_code': coupon.code,
        'discount_type': coupon.discount_type,
        'discount_value': float(coupon.discount_value),
        'original_amount': original_amount,
        'discount_amount': discount_amount,
        'final_amount': final_amount,
        'message': f"Coupon '{coupon.code}' applied! You save ₹{discount_amount:,.2f}"
    })


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
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({'success': False, 'error': 'Please sign in to proceed with enrollment.'}, status=401)
        return redirect(f"{reverse('login')}?next={request.path}")

    course = get_object_or_404(
        Course,
        slug=slug,
        is_active=True
    )

    enrollment = CourseEnrollment.objects.filter(
        user=request.user,
        course=course
    ).first()

    if enrollment and enrollment.payment_status == 'Paid' and enrollment.order_status == 'Confirmed':
        return redirect('enrollment_success', enrollment_id=enrollment.enrollment_id)

    user_phone = (
        request.user.phone
        or getattr(
            getattr(request.user, 'profile', None),
            'phone',
            ''
        )
    )

    if request.method == 'POST':
        is_ajax = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest'
            or 'application/json' in request.headers.get('Accept', '')
        )

        enrollment, _ = CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
        )

        payment_method = request.POST.get('payment_method', 'UPI')
        phone = request.POST.get('phone') or request.POST.get('detail_mobile') or user_phone
        agree_terms = request.POST.get('agree_terms') in ('on', 'true', True, 1, '1')

        if not agree_terms:
            err_msg = 'You must agree to the Terms & Conditions and Refund Policy to continue.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': err_msg}, status=400)
            return render(request, 'skill_global/course_enrollment.html', {
                'page_title': 'Course Enrollment',
                'page_description': 'Complete your enrollment securely.',
                'course': course,
                'enrollment': enrollment,
                'user_full_name': request.user.get_full_name() or request.user.email,
                'user_email': request.user.email,
                'user_phone': user_phone,
                'error': err_msg,
            })

        if not phone:
            err_msg = 'Please enter a valid phone number.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': err_msg}, status=400)
            return render(request, 'skill_global/course_enrollment.html', {
                'page_title': 'Course Enrollment',
                'page_description': 'Complete your enrollment securely.',
                'course': course,
                'enrollment': enrollment,
                'user_full_name': request.user.get_full_name() or request.user.email,
                'user_email': request.user.email,
                'user_phone': user_phone,
                'error': err_msg,
            })

        branch = request.POST.get('detail_branch', '')
        specialization = request.POST.get('detail_specialization', '')
        dob_str = request.POST.get('detail_dob', '')
        address = request.POST.get('detail_address', '')

        date_of_birth = None
        if dob_str:
            try:
                from datetime import datetime
                date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except Exception:
                date_of_birth = None

        if phone:
            if hasattr(request.user, 'phone') and not request.user.phone:
                request.user.phone = phone
                request.user.save(update_fields=['phone'])
            if hasattr(request.user, 'profile') and not request.user.profile.phone:
                request.user.profile.phone = phone
                request.user.profile.save(update_fields=['phone'])

        coupon_code = request.POST.get('coupon_code', '').strip().upper()
        applied_coupon = None
        orig_amount = float(course.price or 0)
        disc_amount = 0.0
        final_amount = orig_amount

        if coupon_code:
            applied_coupon = Coupon.objects.filter(code=coupon_code).first()
            if applied_coupon:
                is_valid, _ = applied_coupon.is_valid(orig_amount)
                if is_valid:
                    disc_amount = applied_coupon.calculate_discount(orig_amount)
                    final_amount = max(0.0, round(orig_amount - disc_amount, 2))

        if not course.price or course.price <= 0 or final_amount <= 0:
            enrollment.payment_method = payment_method or 'Free'
            enrollment.original_amount = orig_amount
            enrollment.discount_amount = disc_amount
            enrollment.amount = 0
            enrollment.coupon = applied_coupon
            enrollment.payment_status = 'Paid'
            enrollment.order_status = 'Confirmed'
            enrollment.branch = branch
            enrollment.specialization = specialization
            enrollment.date_of_birth = date_of_birth
            enrollment.address = address
            enrollment.save()
            if applied_coupon:
                applied_coupon.used_count += 1
                applied_coupon.save(update_fields=['used_count'])
            send_enrollment_confirmation_email(enrollment)

            success_url = reverse('enrollment_success', kwargs={'enrollment_id': enrollment.enrollment_id})
            if is_ajax:
                return JsonResponse({'success': True, 'is_free': True, 'redirect_url': success_url})
            return redirect('enrollment_success', enrollment_id=enrollment.enrollment_id)

        enrollment.payment_method = payment_method
        enrollment.original_amount = orig_amount
        enrollment.discount_amount = disc_amount
        enrollment.amount = final_amount
        enrollment.coupon = applied_coupon
        enrollment.payment_status = 'Pending'
        enrollment.order_status = 'Pending'
        enrollment.branch = branch
        enrollment.specialization = specialization
        enrollment.date_of_birth = date_of_birth
        enrollment.address = address
        enrollment.save()

        try:
            if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
                raise ValueError('Razorpay credentials are not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in your environment or .env file.')

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            amount_paise = int(float(enrollment.amount) * 100)
            razorpay_order = client.order.create({
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': enrollment.enrollment_id,
                'payment_capture': 1,
            })
            enrollment.razorpay_order_id = razorpay_order['id']
            enrollment.save(update_fields=['razorpay_order_id', 'updated_at'])

            return JsonResponse({
                'success': True,
                'is_free': False,
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_amount': amount_paise,
                'razorpay_currency': 'INR',
                'user_full_name': request.user.get_full_name() or request.user.email,
                'user_email': request.user.email,
                'user_phone': phone,
                'course_title': course.title,
            })

        except Exception as exc:
            logger.exception('Razorpay order creation failed for enrollment %s', enrollment.enrollment_id)
            enrollment.payment_status = 'Failed'
            enrollment.order_status = 'Cancelled'
            enrollment.save(update_fields=['payment_status', 'order_status', 'updated_at'])
            err_msg = str(exc) if settings.DEBUG else 'Unable to process payment. Please try again later.'
            return JsonResponse({'success': False, 'error': err_msg}, status=500)

    context = {
        'page_title': 'Course Enrollment',
        'page_description': 'Complete your enrollment securely.',
        'course': course,
        'enrollment': enrollment,
        'user_full_name': request.user.get_full_name() or request.user.email,
        'user_email': request.user.email,
        'user_phone': user_phone,
        'debug': settings.DEBUG,
    }

    return render(request, 'skill_global/course_enrollment.html', context)

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


def enrollment_invoice(request, enrollment_id):
    enrollment = get_object_or_404(CourseEnrollment, enrollment_id=enrollment_id, user=request.user)
    if enrollment.payment_status != 'Paid' or enrollment.order_status != 'Confirmed':
        return redirect('course_enrollment', slug=enrollment.course.slug)

    context = {
        'page_title': f'Tax Invoice #{enrollment.enrollment_id}',
        'page_description': 'Official Course Fee Tax Invoice & Receipt',
        'enrollment': enrollment,
    }
    return render(request, 'skill_global/enrollment_invoice.html', context)


def payment_failed(request):
    reason = request.GET.get('reason')
    context = {
        'page_title': 'Payment Failed',
        'page_description': 'Your payment could not be completed.',
        'payment_cancelled': reason == 'cancelled',
        'payment_message': (
            'Payment Cancelled' if reason == 'cancelled'
            else 'Payment was declined. Please try again.' if reason == 'failed'
            else 'Payment verification failed. Please try again.'
        ),
    }
    return render(request, 'skill_global/payment_failed.html', context)


def razorpay_verify(request):
    """Verify a successful Razorpay response before confirming enrollment."""

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid payment verification request.'}, status=405)

    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    print("=== RAZORPAY VERIFICATION DEBUG ===")
    print("Razorpay Order ID from request:", razorpay_order_id)
    print("Razorpay Payment ID from request:", razorpay_payment_id)
    print("Razorpay Signature from request:", razorpay_signature[:20] + "..." if razorpay_signature else None)

    if not razorpay_payment_id or not razorpay_order_id or not razorpay_signature:
        logger.warning(
            'Razorpay verification received incomplete response: order_id=%s payment_id=%s',
            razorpay_order_id,
            razorpay_payment_id,
        )
        return JsonResponse({'success': False, 'error': 'Missing Razorpay payment details.'}, status=400)

    enrollment = CourseEnrollment.objects.filter(
        razorpay_order_id=razorpay_order_id,
        user=request.user,
    ).first()

    if not enrollment:
        logger.warning(
            'Razorpay verification enrollment not found: order_id=%s user_id=%s',
            razorpay_order_id,
            request.user.id,
        )
        print("ERROR: Enrollment not found for Razorpay order ID:", razorpay_order_id)
        return JsonResponse({'success': False, 'error': 'Enrollment not found for this Razorpay order.'}, status=404)

    print("Enrollment found:", enrollment.enrollment_id)
    print("Enrollment's stored Razorpay Order ID:", enrollment.razorpay_order_id)
    print("Order ID match:", enrollment.razorpay_order_id == razorpay_order_id)

    if enrollment.razorpay_order_id != razorpay_order_id:
        logger.error(
            'Razorpay order mismatch for enrollment %s: callback=%s stored=%s',
            enrollment.enrollment_id,
            razorpay_order_id,
            enrollment.razorpay_order_id,
        )
        return JsonResponse({'success': False, 'error': 'Razorpay order mismatch.'}, status=400)

    if enrollment.payment_status == 'Paid' and enrollment.order_status == 'Confirmed':
        print("Enrollment already paid and confirmed - redirecting to success")
        return JsonResponse({'success': True, 'redirect_url': reverse(
            'enrollment_success', kwargs={'enrollment_id': enrollment.enrollment_id}
        )})

    try:
        print("Attempting Razorpay signature verification...")
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
        print("Razorpay signature verification SUCCESSFUL")

        with transaction.atomic():
            enrollment.razorpay_payment_id = razorpay_payment_id
            enrollment.razorpay_signature = razorpay_signature
            enrollment.payment_status = 'Paid'
            enrollment.order_status = 'Confirmed'
            enrollment.save()
        logger.info(
            'Razorpay payment verified: enrollment=%s order_id=%s payment_id=%s',
            enrollment.enrollment_id,
            razorpay_order_id,
            razorpay_payment_id,
        )
        print("Enrollment updated successfully - payment_status=Paid, order_status=Confirmed")
        if enrollment.coupon:
            enrollment.coupon.used_count += 1
            enrollment.coupon.save(update_fields=['used_count'])
        send_enrollment_confirmation_email(enrollment)

        return JsonResponse({'success': True, 'redirect_url': reverse(
            'enrollment_success', kwargs={'enrollment_id': enrollment.enrollment_id}
        )})

    except razorpay.errors.SignatureVerificationError as e:
        print("RAZORPAY SIGNATURE VERIFICATION FAILED:", str(e))
        logger.warning(
            'Razorpay signature verification failed for enrollment %s: order_id=%s payment_id=%s',
            enrollment.enrollment_id,
            razorpay_order_id,
            razorpay_payment_id,
        )
        enrollment.payment_status = 'Failed'
        enrollment.order_status = 'Cancelled'
        enrollment.save(update_fields=['payment_status', 'order_status', 'updated_at'])
        return JsonResponse({'success': False, 'error': 'Invalid Razorpay payment signature.'}, status=400)
    except Exception as e:
        print("EXCEPTION during Razorpay verification:", str(e))
        logger.exception('Razorpay verification exception for enrollment %s', enrollment.enrollment_id)
        enrollment.payment_status = 'Failed'
        enrollment.order_status = 'Cancelled'
        enrollment.save(update_fields=['payment_status', 'order_status', 'updated_at'])
        return JsonResponse({'success': False, 'error': 'Payment verification failed. Please try again.'}, status=500)



@csrf_exempt
def test_confirm_payment(request, enrollment_id):
    """Direct Instant Test Payment Confirmation Endpoint"""
    enrollment = get_object_or_404(CourseEnrollment, enrollment_id=enrollment_id)
    
    if request.method == 'POST':
        branch = request.POST.get('detail_branch')
        specialization = request.POST.get('detail_specialization')
        dob_str = request.POST.get('detail_dob')
        address = request.POST.get('detail_address')
        phone = request.POST.get('detail_mobile') or request.POST.get('phone')
        
        if branch: enrollment.branch = branch
        if specialization: enrollment.specialization = specialization
        if address: enrollment.address = address
        if phone:
            if hasattr(request.user, 'phone') and not request.user.phone:
                request.user.phone = phone
                request.user.save(update_fields=['phone'])
            if hasattr(request.user, 'profile') and not request.user.profile.phone:
                request.user.profile.phone = phone
                request.user.profile.save(update_fields=['phone'])
        if dob_str:
            try:
                from datetime import datetime
                enrollment.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except Exception:
                pass

    enrollment.payment_status = 'Paid'
    enrollment.order_status = 'Confirmed'
    if not enrollment.razorpay_payment_id:
        import uuid
        enrollment.razorpay_payment_id = f"pay_test_{uuid.uuid4().hex[:12].upper()}"
    if not enrollment.payment_method:
        enrollment.payment_method = 'Test Payment'
    enrollment.save()
    if enrollment.coupon:
        enrollment.coupon.used_count += 1
        enrollment.coupon.save(update_fields=['used_count'])
    send_enrollment_confirmation_email(enrollment)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('enrollment_success', kwargs={'enrollment_id': enrollment.enrollment_id})
        })

    messages.success(request, "Test payment confirmed successfully!")
    return redirect('enrollment_success', enrollment_id=enrollment.enrollment_id)


def check_payment_status(request, order_id):
    """API endpoint to poll payment status and auto-redirect main window if paid"""
    enrollment = CourseEnrollment.objects.filter(razorpay_order_id=order_id).first()
    if enrollment and enrollment.payment_status == 'Paid' and enrollment.order_status == 'Confirmed':
        return JsonResponse({
            'paid': True,
            'redirect_url': reverse('enrollment_success', kwargs={'enrollment_id': enrollment.enrollment_id})
        })
    return JsonResponse({'paid': False})


def course_certificate(request, enrollment_id):
    enrollment = get_object_or_404(CourseEnrollment, enrollment_id=enrollment_id, user=request.user)
    if enrollment.payment_status != 'Paid' or enrollment.order_status != 'Confirmed':
        return redirect('course_enrollment', slug=enrollment.course.slug)

    context = {
        'page_title': f'Official Certificate | {enrollment.course.title}',
        'page_description': 'Skill Global Verified Course Completion Certificate',
        'enrollment': enrollment,
        'student_name': request.user.get_full_name() or request.user.email.split('@')[0].title(),
        'issue_date': enrollment.updated_at or enrollment.created_at,
    }
    return render(request, 'skill_global/course_certificate.html', context)


def my_courses(request):
    if not request.user.is_authenticated:
        return redirect('login')

    enrollments = CourseEnrollment.objects.filter(
        user=request.user,
        payment_status='Paid',
        order_status='Confirmed',
    ).select_related('course').order_by('-created_at')

    # Calculate dashboard metrics
    total_enrolled = enrollments.count()
    completed_courses = 0

    enrollment_list = []
    for idx, item in enumerate(enrollments):
        progress = max(25, min(100, (100 - (idx * 25))))
        if progress >= 80:
            completed_courses += 1
        
        item.progress = progress
        item.is_completed = (progress >= 80)
        item.modules = [
            {
                'num': 1,
                'title': 'Module 1: Foundations & Fundamentals',
                'lessons': '4 Lessons • 2h 30m',
                'status': 'Completed',
                'badge_class': 'bg-success'
            },
            {
                'num': 2,
                'title': 'Module 2: Core Practical Hands-on Labs',
                'lessons': '6 Lessons • 4h 15m',
                'status': 'In Progress' if progress < 100 else 'Completed',
                'badge_class': 'bg-primary' if progress < 100 else 'bg-success'
            },
            {
                'num': 3,
                'title': 'Module 3: Advanced Topics & Capstone Project',
                'lessons': '5 Lessons • 3h 45m',
                'status': 'Upcoming' if progress < 75 else 'In Progress',
                'badge_class': 'bg-secondary' if progress < 75 else 'bg-primary'
            }
        ]
        item.resources = [
            {'title': f'{item.course.title} - Official Complete Study Guide.pdf', 'size': '4.2 MB', 'icon': 'bi-file-earmark-pdf-fill text-danger'},
            {'title': f'Lab Setup Instructions & Code Repository.zip', 'size': '12.8 MB', 'icon': 'bi-file-earmark-zip-fill text-primary'},
            {'title': f'Course Slide Notes & Cheat Sheets.pdf', 'size': '2.1 MB', 'icon': 'bi-file-earmark-slides-fill text-warning'},
        ]
        enrollment_list.append(item)

    context = {
        'page_title': 'My Learning Dashboard',
        'page_description': 'Access your enrolled courses, study materials, certificates, and invoices.',
        'enrollments': enrollment_list,
        'total_enrolled': total_enrolled,
        'active_courses': total_enrolled - completed_courses,
        'completed_courses': completed_courses,
        'user_name': request.user.get_full_name() or request.user.email.split('@')[0].title(),
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
