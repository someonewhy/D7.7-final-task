from celery import shared_task
from celery.schedules import solar, crontab
from .models import Post
from django.core.mail import send_mail
from django.contrib.auth.models import User

from ..NewsPaper.celery import app


@shared_task
def send_notification_email(post_id):
    from .models import Post, Category, User

    try:
        post = Post.objects.get(pk=post_id)
        categories = post.categories.all()
        subscribers = User.objects.filter(subscribed_categories__post=post)

        for subscriber in subscribers:
            subject = post.title
            message = f"Здравствуй, {subscriber.username}. Новая статья в твоем любимом разделе!"
            send_mail(subject, message, 'from_email@example.com', [subscriber.email], fail_silently=True)
    except Post.DoesNotExist:
        pass


@shared_task(run_every=solar.week_starts(weekday=0, hour=8, minute=0))
def send_weekly_newsletter_task():
    posts = Post.objects.filter(post_type='news').order_by('-created_at')[:5]  # Получаем последние 5 новостей
    subscribers = User.objects.filter(subscribed_categories__post__post_type='news').distinct()  # Получаем всех подписчиков новостей

    for subscriber in subscribers:
        subject = "Еженедельная рассылка новостей"
        message = "Добрый день!\n\nВот последние новости:\n\n"
        for post in posts:
            message += f"{post.title}\n{post.content}\n\n"

        message += "С уважением,\nВаш сайт новостей"

        send_mail(subject, message, 'noreply@example.com', [subscriber.email], fail_silently=True)

app.conf.beat_schedule = {
    'send_weekly_newsletter': {
        'task': 'news.tasks.send_weekly_newsletter_task',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),
    },
}