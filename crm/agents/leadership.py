"""
Leadership Pipeline Agent
=========================

Identifies high-potential members and tracks role progressions.

Schedule: Quarterly review
Phase: 3 (stub ready for implementation)
"""

from crm.agents import is_agent_active, log_task, update_agent_run, create_admin_flag

AGENT_NAME = 'leadership'


def quarterly_review():
    """Identify members who may be ready for leadership progression."""
    from crm.models import Member, LeadershipProgression

    if not is_agent_active(AGENT_NAME):
        return

    # Find active members who have been engaged and could move up
    active_members = Member.objects.filter(status='active', role='member')
    candidates = 0

    for member in active_members:
        activity_count = member.activity_logs.count()
        event_count = member.event_attendance.filter(attended=True).count()

        if activity_count >= 5 and event_count >= 2:
            existing = LeadershipProgression.objects.filter(
                member=member, is_approved=False
            ).exists()

            if not existing:
                LeadershipProgression.objects.create(
                    member=member,
                    from_role='member',
                    to_role='foundation_support',
                    reason=(
                        f'High engagement: {activity_count} activities, '
                        f'{event_count} event attendances. '
                        f'Recommended for Foundation Support role.'
                    ),
                    recommended_by='Leadership Pipeline Agent',
                )

                create_admin_flag(
                    flag_type='leadership_candidate',
                    title=f'{member.full_name} recommended for Foundation Support',
                    description=(
                        f'{member.full_name} shows strong engagement with '
                        f'{activity_count} activities and {event_count} events attended. '
                        f'Review for promotion to Foundation Support (The Builders).'
                    ),
                    priority='medium',
                    agent_name=AGENT_NAME,
                    member=member,
                )
                candidates += 1

    update_agent_run(AGENT_NAME)
    log_task(
        AGENT_NAME, 'Quarterly review complete',
        f'Leadership candidates identified: {candidates}', level='info'
    )
