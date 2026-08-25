from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import Course, CourseEnrollment, CustomUser


class LiveClassesViewTests(TestCase):
    def test_live_classes_page_returns_200(self):
        response = self.client.get(reverse('live_classes'))
        self.assertEqual(response.status_code, 200)


class CourseEnrollmentFlowTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='student@example.com',
            password='TestPass123',
            full_name='Student User',
            phone='9876543210',
        )
        self.course = Course.objects.create(
            title='Django Course',
            slug='django-course',
            category='Programming',
            instructor='Instructor A',
            duration='4 weeks',
            description='Learn Django',
            price=1999,
        )

    def test_get_enrollment_page_does_not_create_enrollment_record(self):
        self.client.login(email='student@example.com', password='TestPass123')

        response = self.client.get(reverse('course_enrollment', args=[self.course.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(CourseEnrollment.objects.filter(user=self.user, course=self.course).exists())
        self.assertNotIn('open_razorpay', response.context)

    @patch('skill_global.views.razorpay.Client')
    def test_paid_enrollment_post_creates_pending_order_and_opens_razorpay(self, mock_client):
        self.client.login(email='student@example.com', password='TestPass123')
        mock_client.return_value.order.create.return_value = {'id': 'order_test_123'}

        response = self.client.post(
            reverse('course_enrollment', args=[self.course.slug]),
            {
                'agree_terms': 'on',
                'detail_name': 'Student User',
                'detail_email': 'student@example.com',
                'detail_mobile': '9876543210',
                'detail_dob': '2000-01-15',
                'detail_branch': 'Computer Science',
                'detail_specialization': 'Web Development',
                'detail_address': '123 Main Street',
                'payment_method': 'UPI',
            },
        )

        self.assertEqual(response.status_code, 200)
        enrollment = CourseEnrollment.objects.get(user=self.user, course=self.course)
        self.assertEqual(enrollment.payment_status, 'Pending')
        self.assertEqual(enrollment.order_status, 'Pending')
        self.assertEqual(enrollment.razorpay_order_id, 'order_test_123')
        self.assertTrue(response.context.get('open_razorpay'))

    @patch('skill_global.views.send_enrollment_confirmation_email')
    @patch('skill_global.views.razorpay.Client')
    def test_successful_razorpay_callback_confirms_existing_enrollment(self, mock_client, mock_email):
        self.client.login(email='student@example.com', password='TestPass123')
        enrollment = CourseEnrollment.objects.create(
            user=self.user,
            course=self.course,
            amount=self.course.price,
            razorpay_order_id='order_test_123',
        )
        response = self.client.post(
            reverse('razorpay_verify'),
            {
                'razorpay_payment_id': 'pay_test_123',
                'razorpay_order_id': 'order_test_123',
                'razorpay_signature': 'signature_test_123',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.payment_status, 'Paid')
        self.assertEqual(enrollment.order_status, 'Confirmed')
        self.assertEqual(enrollment.razorpay_payment_id, 'pay_test_123')
        self.assertEqual(enrollment.razorpay_signature, 'signature_test_123')
        self.assertIn(enrollment.enrollment_id, response.json()['redirect_url'])
        mock_client.return_value.utility.verify_payment_signature.assert_called_once_with({
            'razorpay_order_id': 'order_test_123',
            'razorpay_payment_id': 'pay_test_123',
            'razorpay_signature': 'signature_test_123',
        })
        mock_email.assert_called_once_with(enrollment)
