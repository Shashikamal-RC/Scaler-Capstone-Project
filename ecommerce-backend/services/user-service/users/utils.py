"""
Utility functions for the users app.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_password_reset_email(user_email, reset_token, user_name=None):
    """
    Send password reset email to user.
    
    Args:
        user_email (str): User's email address
        reset_token (str): Password reset token
        user_name (str): User's name for personalization
    """
    subject = 'Password Reset Request - E-Commerce Platform'
    
    # Create email content
    context = {
        'user_name': user_name or 'User',
        'reset_token': reset_token,
        'expiry_hours': settings.PASSWORD_RESET_TOKEN_EXPIRY_HOURS,
    }
    
    # For now, simple text email. Can create HTML templates later
    html_message = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hi {context['user_name']},</p>
            <p>You requested to reset your password. Use the token below to reset your password:</p>
            <p><strong>Token: {context['reset_token']}</strong></p>
            <p>This token will expire in {context['expiry_hours']} hours.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <br>
            <p>Thanks,<br>E-Commerce Platform Team</p>
        </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False


def send_email_verification_email(user_email, verification_token, user_name=None):
    """
    Send email verification link to user.
    
    Args:
        user_email (str): User's email address
        verification_token (str): Email verification token
        user_name (str): User's name for personalization
    """
    subject = 'Verify Your Email - E-Commerce Platform'
    
    context = {
        'user_name': user_name or 'User',
        'verification_token': verification_token,
    }
    
    html_message = f"""
    <html>
        <body>
            <h2>Welcome to E-Commerce Platform!</h2>
            <p>Hi {context['user_name']},</p>
            <p>Thank you for registering. Please verify your email address using the token below:</p>
            <p><strong>Token: {context['verification_token']}</strong></p>
            <p>If you didn't create this account, please ignore this email.</p>
            <br>
            <p>Thanks,<br>E-Commerce Platform Team</p>
        </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


def send_password_changed_notification(user_email, user_name=None):
    """
    Send notification email when password is successfully changed.
    
    Args:
        user_email (str): User's email address
        user_name (str): User's name for personalization
    """
    subject = 'Password Changed Successfully - E-Commerce Platform'
    
    context = {
        'user_name': user_name or 'User',
    }
    
    html_message = f"""
    <html>
        <body>
            <h2>Password Changed Successfully</h2>
            <p>Hi {context['user_name']},</p>
            <p>Your password has been changed successfully.</p>
            <p>If you didn't make this change, please contact support immediately.</p>
            <br>
            <p>Thanks,<br>E-Commerce Platform Team</p>
        </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending password changed notification: {e}")
        return False
