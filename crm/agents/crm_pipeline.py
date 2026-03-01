"""
CRM Pipeline Agent
==================

Daily checks for member data quality, inactivity detection, and admin reporting.

Schedule: Daily 9 AM UK time
Phase: 2 (stub ready for implementation)
"""

from datetime import timedelta
from django.utils import timezone
from crm.agents import is_agent_active, log_task, update_agent_run, create_admin_flag

AGENT_NAME = 'crm_pipeline'


def daily_pipeline_check():
    """Daily CRM health check - flags issues for admin review."""
    from crm.models import Member, AdminFlag

    if not is_agent_active(AGENT_NAME):
        return

    now = timezone.now()
    processed = 0

    # Flag members inactive for 90+ days
    inactive_cutoff = (now - timedelta(days=90)).date()
    inactive_members = Member.objects.filter(
        status='active',
        last_engagement_date__lte=inactive_cutoff,
    ).exclude(
        admin_flags__flag_type='inactive_member',
        admin_flags__is_resolved=False,
    )

    for member in inactive_members:
        create_admin_flag(
            flag_type='inactive_member',
            title=f'{member.full_name} inactive for 90+ days',
            description=(
                f'Last engagement: {member.last_engagement_date}. '
                f'Consider reaching out or updating their status.'
            ),
            priority='medium',
            agent_name=AGENT_NAME,
            member=member,
        )
        processed += 1

    # Flag members with missing chamber assignment
    unassigned = Member.objects.filter(
        status='active', chamber__isnull=True
    ).exclude(
        admin_flags__flag_type='missing_data',
        admin_flags__is_resolved=False,
    )

    for member in unassigned:
        create_admin_flag(
            flag_type='missing_data',
            title=f'{member.full_name} has no chamber assigned',
            description='Active member without a chamber assignment.',
            priority='low',
            agent_name=AGENT_NAME,
            member=member,
        )
        processed += 1

    update_agent_run(AGENT_NAME)
    log_task(AGENT_NAME, 'Daily pipeline check complete', f'Flags created: {processed}')
