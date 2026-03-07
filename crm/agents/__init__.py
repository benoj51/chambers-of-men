"""
The Chambers of Men - Agent Framework
======================================

Automated agents that handle onboarding, CRM pipeline management,
event management, Iron Circle assignment, social media, and
leadership development.

Each agent is a module with tasks that can be triggered by:
- Django signals (immediate, e.g. new signup)
- Django-Q scheduled tasks (cron-based, e.g. daily checks)
- Manual admin actions

All agents check their AgentConfig before running - if the agent
is paused in the admin, the task exits gracefully.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context

logger = logging.getLogger('chambers.agents')


def is_agent_active(agent_name):
    """Check if an agent is enabled in the AgentConfig."""
    from crm.models import AgentConfig
    try:
        config = AgentConfig.objects.get(agent_name=agent_name)
        return config.is_active
    except AgentConfig.DoesNotExist:
        return False


def log_task(agent_name, action, detail='', level='info', member=None,
             email_sent_to='', template_used=''):
    """Create a TaskLog entry for audit trail."""
    from crm.models import TaskLog
    TaskLog.objects.create(
        agent_name=agent_name,
        action=action,
        detail=detail,
        level=level,
        member=member,
        email_sent_to=email_sent_to,
        template_used=template_used,
    )
    log_method = getattr(logger, level, logger.info)
    log_method(f"[{agent_name}] {action} - {detail}")


def update_agent_run(agent_name):
    """Update the last_run timestamp and increment run_count."""
    from crm.models import AgentConfig
    try:
        config = AgentConfig.objects.get(agent_name=agent_name)
        config.last_run = timezone.now()
        config.run_count += 1
        config.save(update_fields=['last_run', 'run_count', 'updated_at'])
    except AgentConfig.DoesNotExist:
        pass


def send_template_email(template_key, recipient_email, context_data=None):
    """Send an email using a stored EmailTemplate."""
    from crm.models import EmailTemplate
    context_data = context_data or {}

    try:
        template = EmailTemplate.objects.get(template_key=template_key, is_active=True)
    except EmailTemplate.DoesNotExist:
        logger.error(f"Email template '{template_key}' not found or inactive")
        return False

    subject, body_html, body_text = template.render(context_data)

    if not body_text:
        import re
        body_text = re.sub(r'<[^>]+>', '', body_html)
        body_text = re.sub(r'\n\s*\n', '\n\n', body_text).strip()

    from_email = f"{template.from_name} <{template.from_email}>"

    try:
        msg = EmailMultiAlternatives(
            subject=subject, body=body_text,
            from_email=from_email, to=[recipient_email],
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send()
        return True
    except Exception as e:
        logger.error(f"Failed to send email '{template_key}' to {recipient_email}: {e}")
        return False


def create_admin_flag(flag_type, title, description='', priority='medium',
                      agent_name='', member=None):
    """Create an AdminFlag for admin review."""
    from crm.models import AdminFlag
    AdminFlag.objects.create(
        flag_type=flag_type, title=title,
        description=description, priority=priority,
        agent_name=agent_name, member=member,
    )
