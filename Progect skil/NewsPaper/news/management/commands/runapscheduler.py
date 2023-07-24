import logging
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail
from django.utils import timezone
from NewsPaper.news.helpers import send_notification_email
from NewsPaper.news.models import Category, Post

logger = logging.getLogger(__name__)

def my_job():
    # Получаем все категории, которые существуют в системе
    all_categories = Category.objects.all()

    for category in all_categories:
        # Получаем всех подписчиков этой категории
        subscribers = category.subscribers.all()

        # Получаем все статьи в этой категории, опубликованные за последнюю неделю
        new_posts = Post.objects.filter(
            categories=category,
            created_at__gte=timezone.now() - timezone.timedelta(weeks=1),
        )

        # Отправляем уведомление каждому подписчику с новыми статьями
        for subscriber in subscribers:
            send_notification_email(subscriber, new_posts)


def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(second="*/10"),
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
