from django.conf import settings
from django.core.mail import send_mail

from .models import Category, Post, User
from datetime import timedelta

def send_notification_email(user, posts):
    # Формируем текст письма с новыми статьями/постами
    subject = "Weekly News Digest"
    message = f"Hello, {user.username}! Here are the new posts in your favorite categories:\n\n"
    for post in posts:
        message += f"- {post.title}\n"
    message += "\nThank you for subscribing to our newsletter!"

    # Отправляем письмо
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)