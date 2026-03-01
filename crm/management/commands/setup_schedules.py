"""
Management command to create Django-Q scheduled tasks for all agents.

Usage:
    python manage.py setup_schedules
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Set up Django-Q scheduled tasks for all agents'

    def handle(self, *args, **options):
        try:
            from django_q.models import Schedule
        except ImportError:
            self.stdout.write(self.style.ERROR(
                'Django-Q is not installed. Run: pip install django-q2'
            ))
            return

        schedules = [
            {
                'name': 'Onboarding Agent - Daily Follow-ups',
                'func': 'crm.agents.onboarding.process_follow_ups',
                'schedule_type': Schedule.CRON,
                'cron': '0 9 * * *',  # Daily at 9 AM
            },
            {
                'name': 'CRM Pipeline Agent - Daily Check',
                'func': 'crm.agents.crm_pipeline.daily_pipeline_check',
                'schedule_type': Schedule.CRON,
                'cron': '0 9 * * *',  # Daily at 9 AM
            },
            {
                'name': 'Event Manager Agent - Daily Check',
                'func': 'crm.agents.event_manager.daily_event_check',
                'schedule_type': Schedule.CRON,
                'cron': '0 8 * * *',  # Daily at 8 AM
            },
            {
                'name': 'Iron Circle Agent - Monthly Review',
                'func': 'crm.agents.iron_circle.monthly_circle_review',
                'schedule_type': Schedule.CRON,
                'cron': '0 9 1 * *',  # 1st of each month at 9 AM
            },
            {
                'name': 'Social Media Agent - Weekly Check',
                'func': 'crm.agents.social_media.weekly_content_check',
                'schedule_type': Schedule.CRON,
                'cron': '0 10 * * 1,3,5',  # Mon, Wed, Fri at 10 AM
            },
            {
                'name': 'Leadership Agent - Quarterly Review',
                'func': 'crm.agents.leadership.quarterly_review',
                'schedule_type': Schedule.CRON,
                'cron': '0 9 1 1,4,7,10 *',  # 1st of Jan, Apr, Jul, Oct
            },
        ]

        for sched_data in schedules:
            obj, created = Schedule.objects.get_or_create(
                name=sched_data['name'],
                defaults={
                    'func': sched_data['func'],
                    'schedule_type': sched_data['schedule_type'],
                    'cron': sched_data['cron'],
                }
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f"  {status}: {obj.name}")

        self.stdout.write(self.style.SUCCESS('All schedules configured.'))
