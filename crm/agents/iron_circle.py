"""
Iron Circle Management Agent
=============================

Handles circle member matching, capacity alerts, and meeting reminders.

Schedule: Monthly on 1st + triggered when member becomes active
Phase: 3 (stub ready for implementation)
"""

from crm.agents import (
    is_agent_active, log_task, update_agent_run,
    send_template_email, create_admin_flag,
)

AGENT_NAME = 'iron_circle'


def match_member_to_circle(member_id):
    """Match a newly active member to an open Iron Circle by city."""
    from crm.models import Member, IronCircle, CircleAssignmentHistory

    if not is_agent_active(AGENT_NAME):
        return

    try:
        member = Member.objects.get(id=member_id)
    except Member.DoesNotExist:
        return

    circles = IronCircle.objects.filter(
        is_open=True, chamber__city=member.city
    ).order_by('members')

    if not circles.exists():
        circles = IronCircle.objects.filter(is_open=True).order_by('members')

    for circle in circles:
        if not circle.is_full:
            circle.members.add(member)
            CircleAssignmentHistory.objects.create(
                member=member, circle=circle,
                action='joined', performed_by='Iron Circle Agent',
            )
            context = {
                'name': member.full_name, 'first_name': member.first_name,
                'circle_name': circle.name,
                'leader_name': circle.circle_leader.full_name if circle.circle_leader else 'your circle leader',
            }
            send_template_email('circle_welcome', member.email, context)
            log_task(
                AGENT_NAME, f'Member assigned to {circle.name}',
                f'{member.full_name} joined {circle.name}',
                level='success', member=member,
                email_sent_to=member.email, template_used='circle_welcome'
            )
            if circle.is_full:
                circle.is_open = False
                circle.save()
                create_admin_flag(
                    flag_type='circle_capacity',
                    title=f'{circle.name} is now at capacity',
                    description=f'{circle.name} has reached {circle.max_members} members.',
                    priority='low', agent_name=AGENT_NAME,
                )
            update_agent_run(AGENT_NAME)
            return

    create_admin_flag(
        flag_type='circle_capacity',
        title=f'No open circle for {member.full_name}',
        description=(
            f'{member.full_name} from {member.city or "unknown city"} '
            f'needs a circle but none are available.'
        ),
        priority='high', agent_name=AGENT_NAME, member=member,
    )
    log_task(AGENT_NAME, 'No circle available', f'For: {member.full_name}', level='warning', member=member)


def monthly_circle_review():
    """Monthly check on circle health."""
    from crm.models import IronCircle
    if not is_agent_active(AGENT_NAME):
        return
    for circle in IronCircle.objects.all():
        if circle.member_count == 0:
            create_admin_flag(
                flag_type='circle_capacity',
                title=f'{circle.name} has no members',
                description='Consider merging or closing this circle.',
                priority='low', agent_name=AGENT_NAME,
            )
    update_agent_run(AGENT_NAME)
    log_task(AGENT_NAME, 'Monthly circle review complete')
