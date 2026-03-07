"""
Event Management Agent
======================

Sends event reminders and post-event follow-ups.

Schedule: Daily 8 AM UK time
Phase: 2 (stub ready for implementation)
"""

from datetime import timedelta
from django.utils import timezone
from crm.agents import (
    is_agent_active, log_task, update_agent_run,
    send_template_email, create_admin_flag,
)

AGENT_NAME = 'event_manager'


def daily_event_check():
    """Check for upcoming events and send reminders."""
    from crm.models import Event, Member

    if not is_agent_active(AGENT_NAME):
        return

    today = timezone.now().date()
    processed = 0

    seven_days = today + timedelta(days=7)
    events_7d = Event.objects.filter(date=seven_days, is_published=True)

    for event in events_7d:
        for member in Member.objects.filter(status='active'):
            context = {
                'name': member.full_name, 'first_name': member.first_name,
                'event_name': event.name,
                'event_date': event.date.strftime('%A %d %B %Y'),
                'event_location': event.location,
            }
            sent = send_template_email('event_reminder_7d', member.email, context)
            if sent:
                log_task(AGENT_NAME, '7-day reminder', f'{event.name} -> {member.full_name}',
                    level='success', member=member, email_sent_to=member.email, template_used='event_reminder_7d')
                processed += 1

    tomorrow = today + timedelta(days=1)
    for event in Event.objects.filter(date=tomorrow, is_published=True):
        for member in Member.objects.filter(status='active'):
            context = {
                'name': member.full_name, 'first_name': member.first_name,
                'event_name': event.name,
                'event_date': event.date.strftime('%A %d %B %Y'),
                'event_location': event.location,
            }
            sent = send_template_email('event_reminder_1d', member.email, context)
            if sent:
                log_task(AGENT_NAME, '1-day reminder', f'{event.name} -> {member.full_name}',
                    level='success', member=member, email_sent_to=member.email, template_used='event_reminder_1d')
                processed += 1

    yesterday = today - timedelta(days=1)
    for event in Event.objects.filter(date=yesterday, is_published=True):
        for record in event.attendance_records.filter(attended=True).select_related('member'):
            member = record.member
            context = {' name': member.full_name, 'first_name': member.first_name, 'event_name': event.name}
            sent = send_template_email('event_thank_you', member.email, context)
            if sent:
                log_task(AGENT_NAME, 'Post-event thank you', f'{event.name} -> {member.full_name}',
                    level='success', member=member, email_sent_to=member.email, template_used='event_thank_you')
                processed += 1

    update_agent_run(AGENT_NAME)
    log_task(AGENT_NAME, 'Daily event check complete', f'Emails sent: {processed}')
