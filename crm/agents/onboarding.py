"""
Onboarding Agent
================

Handles the automated welcome and follow-up email sequence for new signups.

Trigger: Django signal on ContactSubmission.post_save (immediate welcome email)
Schedule: Daily 9 AM UK time (process follow-ups for Day 2, 5, 10)

Sequence:
    1. New signup -> Welcome email (immediate)
    2. Day 2 -> Follow-up asking about faith background
    3. Day 5 -> Invite to intro call with Iron Circle info
    4. Day 10 -> Final follow-up if no response
    5. 24hr before interview -> Interview reminder
"""

from datetime import timedelta
from django.utils import timezone
from crm.agents import (
    is_agent_active, log_task, update_agent_run,
    send_template_email, create_admin_flag,
)

AGENT_NAME = 'onboarding'


def process_new_signup(submission_id):
    """
    Called immediately when a new ContactSubmission is created.
    Sends welcome email and creates a Member record.
    """
    from crm.models import ContactSubmission, Member

    if not is_agent_active(AGENT_NAME):
        return

    try:
        submission = ContactSubmission.objects.get(id=submission_id)
    except ContactSubmission.DoesNotExist:
        log_task(AGENT_NAME, 'Signup not found', f'ID: {submission_id}', level='error')
        return

    # Parse name
    name_parts = submission.name.strip().split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''

    # Create or get Member record
    member, created = Member.objects.get_or_create(
        email=submission.email,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'phone': submission.phone,
            'city': submission.city,
            'reason_for_joining': submission.message,
            'how_heard': _map_how_heard(submission.how_heard),
            'status': 'prospect',
            'onboarding_status': 'not_started',
        }
    )

    if not created:
        log_task(
            AGENT_NAME, 'Member already exists',
            f'{submission.name} ({submission.email}) - skipping welcome email',
            level='info', member=member
        )
        submission.is_processed = True
        submission.save()
        return

    # Send welcome email
    context = {
        'name': submission.name,
        'first_name': first_name,
        'email': submission.email,
        'city': submission.city or 'your area',
    }

    sent = send_template_email('welcome', submission.email, context)

    if sent:
        member.onboarding_status = 'welcome_sent'
        member.save(update_fields=['onboarding_status', 'updated_at'])
        log_task(
            AGENT_NAME, 'Welcome email sent',
            f'To: {submission.name} ({submission.email})',
            level='success', member=member,
            email_sent_to=submission.email, template_used='welcome'
        )
    else:
        log_task(
            AGENT_NAME, 'Welcome email failed',
            f'To: {submission.name} ({submission.email})',
            level='error', member=member, email_sent_to=submission.email
        )

    # Mark submission as processed
    submission.is_processed = True
    submission.save()

    update_agent_run(AGENT_NAME)


def process_follow_ups():
    """
    Daily scheduled task - checks for members who need follow-up emails.
    Runs at 9 AM UK time via Django-Q schedule.
    """
    from crm.models import Member

    if not is_agent_active(AGENT_NAME):
        return

    now = timezone.now()
    processed = 0

    # Day 2 follow-ups: members with welcome_sent, created 2+ days ago
    day_2_cutoff = now - timedelta(days=2)
    day_2_members = Member.objects.filter(
        onboarding_status='welcome_sent',
        created_at__lte=day_2_cutoff,
    )

    for member in day_2_members:
        context = _build_member_context(member)
        sent = send_template_email('follow_up_day_2', member.email, context)
        if sent:
            member.onboarding_status = 'follow_up_1'
            member.save(update_fields=['onboarding_status', 'updated_at'])
            log_task(
                AGENT_NAME, 'Day 2 follow-up sent',
                f'To: {member.full_name} ({member.email})',
                level='success', member=member,
                email_sent_to=member.email, template_used='follow_up_day_2'
            )
            processed += 1

    # Day 5 follow-ups: members with follow_up_1, created 5+ days ago
    day_5_cutoff = now - timedelta(days=5)
    day_5_members = Member.objects.filter(
        onboarding_status='follow_up_1',
        created_at__lte=day_5_cutoff,
    )

    for member in day_5_members:
        context = _build_member_context(member)
        sent = send_template_email('follow_up_day_5', member.email, context)
        if sent:
            member.onboarding_status = 'follow_up_2'
            member.save(update_fields=['onboarding_status', 'updated_at'])
            log_task(
                AGENT_NAME, 'Day 5 follow-up sent',
                f'To: {member.full_name} ({member.email})',
                level='success', member=member,
                email_sent_to=member.email, template_used='follow_up_day_5'
            )
            processed += 1

    # Day 10 final follow-ups: members with follow_up_2, created 10+ days ago
    day_10_cutoff = now - timedelta(days=10)
    day_10_members = Member.objects.filter(
        onboarding_status='follow_up_2',
        created_at__lte=day_10_cutoff,
    )

    for member in day_10_members:
        context = _build_member_context(member)
        sent = send_template_email('follow_up_day_10', member.email, context)
        if sent:
            member.onboarding_status = 'follow_up_3'
            member.save(update_fields=['onboarding_status', 'updated_at'])
            log_task(
                AGENT_NAME, 'Day 10 final follow-up sent',
                f'To: {member.full_name} ({member.email})',
                level='success', member=member,
                email_sent_to=member.email, template_used='follow_up_day_10'
            )
            processed += 1

    # Flag stalled onboarding: follow_up_3 sent 7+ days ago with no progression
    stalled_cutoff = now - timedelta(days=17)  # 10 days + 7 days grace
    stalled_members = Member.objects.filter(
        onboarding_status='follow_up_3',
        created_at__lte=stalled_cutoff,
    )

    for member in stalled_members:
        # Check if flag already exists
        from crm.models import AdminFlag
        existing = AdminFlag.objects.filter(
            flag_type='onboarding_stalled',
            member=member,
            is_resolved=False,
        ).exists()

        if not existing:
            create_admin_flag(
                flag_type='onboarding_stalled',
                title=f'Onboarding stalled for {member.full_name}',
                description=(
                    f'{member.full_name} ({member.email}) completed the full '
                    f'email sequence but has not progressed to an interview. '
                    f'Consider a personal phone call or removal from the pipeline.'
                ),
                priority='medium',
                agent_name=AGENT_NAME,
                member=member,
            )
            log_task(
                AGENT_NAME, 'Onboarding stalled flag created',
                f'For: {member.full_name}', level='warning', member=member
            )

    # Interview reminders: 24hr before scheduled interview
    tomorrow_start = now + timedelta(hours=20)
    tomorrow_end = now + timedelta(hours=28)
    interview_members = Member.objects.filter(
        onboarding_status='interview_scheduled',
        interview_scheduled_date__range=(tomorrow_start, tomorrow_end),
    )

    for member in interview_members:
        context = _build_member_context(member)
        if member.interview_scheduled_date:
            context['interview_date'] = member.interview_scheduled_date.strftime('%A %d %B at %I:%M %p')

        sent = send_template_email('interview_reminder', member.email, context)
        if sent:
            log_task(
                AGENT_NAME, 'Interview reminder sent',
                f'To: {member.full_name} - interview on {member.interview_scheduled_date}',
                level='success', member=member,
                email_sent_to=member.email, template_used='interview_reminder'
            )
            processed += 1

    update_agent_run(AGENT_NAME)

    log_task(
        AGENT_NAME, 'Daily follow-up run complete',
        f'Processed {processed} follow-ups', level='info'
    )


def _build_member_context(member):
    """Build template context from a Member instance."""
    return {
        'name': member.full_name,
        'first_name': member.first_name,
        'email': member.email,
        'city': member.city or 'your area',
    }


def _map_how_heard(how_heard_str):
    """Map free-text how_heard from form to model choices."""
    mapping = {
        'social media': 'social_media',
        'social_media': 'social_media',
        'church': 'church',
        'friend': 'friend',
        'word of mouth': 'friend',
        'event': 'event',
        'website': 'website',
    }
    return mapping.get(how_heard_str.lower().strip(), 'other') if how_heard_str else ''
