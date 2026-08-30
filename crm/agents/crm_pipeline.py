"""
CRM Pipeline Agent
==================

Daily checks for member data quality, inactivity detection, and admin reporting.

Schedule: Daily 9 AM UK time
Phase: 2 (stub ready for implementation)
"""

from datetime import timedelta
from django.utils import timezone
from crm.agents import (
    agent_setting, is_agent_active, log_task, update_agent_run, create_admin_flag,
)

AGENT_NAME = 'crm_pipeline'


def daily_pipeline_check():
    """Daily CRM health check - flags issues for admin review."""
    from crm.models import Member

    if not is_agent_active(AGENT_NAME):
        return

    now = timezone.now()
    processed = 0

    # Flag members inactive for the configured threshold (default 90 days).
    # create_admin_flag is idempotent, so re-flagging is handled there rather
    # than with an exclude() across a multi-valued relation.
    threshold_days = agent_setting(AGENT_NAME, 'inactive_threshold_days', 90)
    inactive_cutoff = now - timedelta(days=threshold_days)
    inactive_members = Member.objects.filter(
        status='active',
        last_activity_date__lte=inactive_cutoff,
    )

    for member in inactive_members:
        flag = create_admin_flag(
            flag_type='inactive_member',
            title=f'{member.full_name} inactive for {threshold_days}+ days',
            description=(
                f'Last activity: {member.last_activity_date:%d %B %Y}. '
                f'Consider reaching out or updating their status.'
            ),
            priority='medium',
            agent_name=AGENT_NAME,
            member=member,
        )
        if flag is not None:
            processed += 1

    # Flag members with missing chamber assignment
    unassigned = Member.objects.filter(status='active', chamber__isnull=True)

    for member in unassigned:
        flag = create_admin_flag(
            flag_type='missing_data',
            title=f'{member.full_name} has no chamber assigned',
            description='Active member without a chamber assignment.',
            priority='low',
            agent_name=AGENT_NAME,
            member=member,
        )
        if flag is not None:
            processed += 1

    update_agent_run(AGENT_NAME)
    log_task(AGENT_NAME, 'Daily pipeline check complete', f'Flags created: {processed}')
