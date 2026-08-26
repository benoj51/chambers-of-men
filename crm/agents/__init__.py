"""
Chambers of Men - Agent Framework
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
import re

from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

logger = logging.getLogger('chambers.agents')


def get_agent_config(agent_name):
    """Return the AgentConfig row for ``agent_name``, or None."""
    from crm.models import AgentConfig
    return AgentConfig.objects.filter(agent_name=agent_name).first()


def is_agent_active(agent_name):
    """Check if an agent is enabled in the AgentConfig."""
    config = get_agent_config(agent_name)
    return bool(config and config.is_active)


def agent_setting(agent_name, key, default=None):
    """Read a value out of an agent's JSON config, with a fallback."""
    config = get_agent_config(agent_name)
    if not config or not isinstance(config.config, dict):
        return default
    return config.config.get(key, default)


def log_task(agent_name, task_name, message='', level='info', member=None,
             email_sent_to='', template_used='', **extra):
    """Create a TaskLog entry for the audit trail.

    ``email_sent_to`` and ``template_used`` are stored inside the ``details``
    JSON field rather than as dedicated columns.
    """
    from crm.models import TaskLog

    details = dict(extra)
    if email_sent_to:
        details['email_sent_to'] = email_sent_to
    if template_used:
        details['template_used'] = template_used

    TaskLog.objects.create(
        agent_name=agent_name,
        task_name=task_name,
        message=message,
        level=level,
        member=member,
        details=details,
    )
    log_method = getattr(logger, level, None)
    if not callable(log_method):
        log_method = logger.info
    log_method(f"[{agent_name}] {task_name} - {message}")


def update_agent_run(agent_name):
    """Update the last_run timestamp and increment run_count."""
    from crm.models import AgentConfig

    config = AgentConfig.objects.filter(agent_name=agent_name).first()
    if not config:
        return
    config.last_run = timezone.now()
    config.run_count += 1
    config.save(update_fields=['last_run', 'run_count', 'updated_at'])


def html_to_text(html):
    """Crude HTML -> plain text fallback for the multipart alternative."""
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.S | re.I)
    text = re.sub(r'<br\s*/?>|</p>|</div>|</h[1-6]>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\n\s*\n\s*\n+', '\n\n', text).strip()


def send_template_email(template_key, recipient_email, context_data=None):
    """Send an email using a stored EmailTemplate. Returns True on success."""
    from crm.models import EmailTemplate

    if not recipient_email:
        logger.error(f"No recipient for email template '{template_key}'")
        return False

    template = EmailTemplate.objects.filter(
        template_key=template_key, is_active=True
    ).first()
    if template is None:
        logger.error(f"Email template '{template_key}' not found or inactive")
        return False

    subject, body_html, body_text = template.render(context_data or {})
    if not body_text:
        body_text = html_to_text(body_html)

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=template.sender,
            to=[recipient_email],
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send()
        return True
    except Exception as e:
        logger.error(f"Failed to send email '{template_key}' to {recipient_email}: {e}")
        return False


def create_admin_flag(flag_type, title, description='', priority='medium',
                      agent_name='', member=None):
    """Create an AdminFlag for admin review.

    Idempotent: if an unresolved flag of the same type already exists for the
    same member, nothing is created. Without this the daily agents would raise
    a duplicate flag on every run.
    """
    from crm.models import AdminFlag

    existing = AdminFlag.objects.filter(
        flag_type=flag_type, member=member, is_resolved=False
    )
    if member is None:
        existing = existing.filter(title=title)
    if existing.exists():
        return None

    return AdminFlag.objects.create(
        flag_type=flag_type,
        title=title,
        description=description,
        priority=priority,
        agent_name=agent_name,
        member=member,
    )
