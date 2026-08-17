# Skill Global - Payment Integration Guide

## Razorpay Payment Implementation

This guide explains how to use and test the Razorpay payment integration in the Skill Global e-learning platform.

## Overview

The payment system integrates Razorpay, a leading Indian payment gateway, to handle course enrollments. It supports multiple payment methods including UPI, Credit/Debit Cards, and Net Banking.

## Setup Instructions

### 1. Install Dependencies

```bash
cd e_study
pip install -r requirements.txt
```

### 2. Configure Razorpay Credentials

Update your `e_study/settings.py`:

```python
# RAZORPAY PAYMENT GATEWAY
RAZORPAY_KEY_ID = "your_test_or_live_key_id"
RAZORPAY_KEY_SECRET = "your_test_or_live_key_secret"
```

Get your credentials from: https://dashboard.razorpay.com/

### 3. Database Migration

If you're setting up for the first time:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Payment Flow

### For Free Courses
1. User clicks "Enroll Now"
2. Fills phone number
3. Accepts terms & conditions
4. Enrollment is confirmed immediately
5. Redirects to success page

### For Paid Courses
1. User clicks "Proceed to Payment"
2. Fills phone number and selects payment method
3. Accepts terms & conditions
4. Clicks "Proceed to Payment"
5. Razorpay checkout opens automatically
6. User completes payment with their chosen method
7. After successful payment:
   - Signature is verified server-side
   - Enrollment is confirmed
   - User sees success page with enrollment details

## Testing the Payment System

### Test Credentials

Use these test card numbers when in test mode:

**Successful Payment:**
- Card Number: 4111 1111 1111 1111
- Expiry: Any future date
- CVV: Any 3 digits
- OTP: 123456

**Failed Payment:**
- Card Number: 4000 0000 0000 0002
- Expiry: Any future date
- CVV: Any 3 digits

### Step-by-Step Test

1. **Start the server:**
   ```bash
   python manage.py runserver
   ```

2. **Navigate to a paid course:**
   - Go to http://127.0.0.1:8000/courses/
   - Click on a course with a price

3. **Click "Enroll" button**

4. **Fill the enrollment form:**
   - Phone: Enter a 10-digit number (e.g., 9876543210)
   - Payment Method: Select UPI, Card, or Net Banking
   - Check the Terms & Conditions checkbox

5. **Click "Proceed to Payment"**

6. **Complete payment in Razorpay checkout:**
   - If using test card, enter test card details
   - For UPI: Use any UPI ID format (e.g., test@upi)
   - Follow prompts to complete payment

7. **Verify enrollment:**
   - You should see the enrollment success page
   - Check "My Courses" to confirm enrollment

## File Structure

```
skill_global/
├── models.py              # CourseEnrollment model
├── views.py               # course_enroll, razorpay_verify views
├── urls.py                # Payment routes
└── templates/
    └── skill_global/
        ├── course_enrollment.html      # Enrollment & payment form
        ├── enrollment_success.html     # Success page
        └── payment_failed.html         # Failure page
```

## Key Functions

### Views

**course_enroll(request, slug)**
- Displays enrollment form
- Creates Razorpay order for paid courses
- Validates phone number and terms agreement
- Returns template with checkout script

**razorpay_verify(request)**
- Verifies payment signature
- Confirms enrollment on success
- Handles payment failures

### Models

**CourseEnrollment**
- `razorpay_order_id`: Order ID from Razorpay
- `razorpay_payment_id`: Payment ID after successful payment
- `razorpay_signature`: Signature for verification
- `payment_status`: Pending/Paid/Failed
- `order_status`: Pending/Confirmed/Cancelled

## Troubleshooting

### Payment Modal Doesn't Open
- Check browser console for JavaScript errors
- Verify Razorpay key is correct in settings.py
- Ensure Razorpay script loads: `https://checkout.razorpay.com/v1/checkout.js`

### Signature Verification Fails
- Verify key_id and key_secret are correct
- Check payment details match exactly (amount, order_id, payment_id)
- Clear browser cache and try again

### Phone Number Validation Error
- Enter exactly 10 digits
- Remove spaces or special characters
- Example: 9876543210

### Enrollment Already Exists Error
- User is already enrolled in this course
- Go to "My Courses" to access the course
- Or enroll in a different course

## Security Considerations

1. **Never expose secret key** in frontend code
2. **Always verify signature** server-side
3. **Use HTTPS** in production
4. **Validate phone number** format
5. **Check user authentication** before enrollment
6. **Log payment transactions** for audit trail
7. **Handle errors gracefully** without exposing sensitive data

## Switching from Test to Production

1. Update `RAZORPAY_KEY_ID` with live key
2. Update `RAZORPAY_KEY_SECRET` with live secret
3. Test thoroughly before going live
4. Monitor payment transactions
5. Set up email/SMS notifications
6. Enable webhook for real-time updates

## Support

For Razorpay support:
- Documentation: https://razorpay.com/docs/
- Dashboard: https://dashboard.razorpay.com/
- Support: support@razorpay.com

## Additional Features (Future)

- [ ] Email receipts after payment
- [ ] Invoice generation
- [ ] Refund management interface
- [ ] Payment retry mechanism
- [ ] Webhook integration
- [ ] SMS notifications
- [ ] Multiple currency support
- [ ] Subscription/recurring payments
