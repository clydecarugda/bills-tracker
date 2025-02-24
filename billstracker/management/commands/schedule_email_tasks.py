from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

class Command(BaseCommand):
    help = "Schedules the due date email notification task in Celery Beat"

    def handle(self, *args, **kwargs):
        # Create an interval schedule (if not already created)
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.DAYS,  # Runs every 1 day
        )

        # Create or update the periodic task
        task_name = "send_due_notifications_daily"
        task, task_created = PeriodicTask.objects.update_or_create(
            name=task_name,
            defaults={
                "interval": schedule,
                "task": "notifications.tasks.send_due_date_reminder",
                "args": json.dumps([]),  # No arguments needed
                "kwargs": json.dumps({}),
                "enabled": True,
            },
        )

        if task_created:
            self.stdout.write(self.style.SUCCESS(f"Created periodic task: {task_name}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated existing periodic task: {task_name}"))
