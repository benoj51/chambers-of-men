"""Template tags backing the Chambers admin dashboard.

The stock admin index is a bare list of models, which says nothing about what
needs attention. This supplies the operational summary rendered above it:
signups waiting, flags raised by the agents, and whether the agents are
actually running.

Everything here is a plain COUNT or a small LIMITed queryset, so the dashboard
adds a fixed handful of cheap queries rather than scaling with the data.
"""

from datetime import timedelta

from django import template
from django.db.models import Count, Q
from django.urls import reverse
from django.utils import timezone

from crm.models import (
    AdminFlag, AgentConfig, ContactSubmission, Event, IronCircle, Member, TaskLog,
)

register = template.Library()

# Agents the project ships with, so the dashboard can report one that has never
# been seeded rather than simply omitting it.
EXPECTED_AGENTS = [
    'onboarding', 'crm_pipeline', 'event_manager',
    'iron_circle', 'social_media', 'leadership',
]


def _changelist(model, **params):
    """URL for a model's changelist, optionally pre-filtered."""
    url = reverse(f'admin:crm_{model}_changelist')
    if params:
        url += '?' + '&'.join(f'{k}={v}' for k, v in params.items())
    return url


@register.inclusion_tag('admin/chambers_dashboard.html', takes_context=True)
def chambers_dashboard(context):
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)

    # --- headline counts ---------------------------------------------------
    unprocessed = ContactSubmission.objects.filter(is_processed=False).count()
    open_flags = AdminFlag.objects.filter(is_resolved=False).count()
    urgent_flags = AdminFlag.objects.filter(
        is_resolved=False, priority__in=('urgent', 'high')
    ).count()

    member_counts = Member.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(status='active')),
        prospects=Count('id', filter=Q(status='prospect')),
    )

    recent_errors = TaskLog.objects.filter(
        level='error', created_at__gte=week_ago
    ).count()

    # --- agent health ------------------------------------------------------
    configs = {c.agent_name: c for c in AgentConfig.objects.all()}
    agents = []
    for name in EXPECTED_AGENTS:
        config = configs.get(name)
        agents.append({
            'name': name.replace('_', ' ').title(),
            'configured': config is not None,
            'is_active': bool(config and config.is_active),
            'last_run': config.last_run if config else None,
            'run_count': config.run_count if config else 0,
        })
    # Any agent seeded under a name not in EXPECTED_AGENTS still deserves a row.
    for name, config in configs.items():
        if name not in EXPECTED_AGENTS:
            agents.append({
                'name': name.replace('_', ' ').title(),
                'configured': True,
                'is_active': config.is_active,
                'last_run': config.last_run,
                'run_count': config.run_count,
            })

    return {
        'cards': [
            {
                'num': unprocessed,
                'label': 'Signups waiting',
                'url': _changelist('contactsubmission', is_processed__exact=0),
                'state': 'attention' if unprocessed else 'good',
            },
            {
                'num': open_flags,
                'label': 'Open flags',
                'url': _changelist('adminflag', is_resolved__exact=0),
                'state': 'attention' if urgent_flags else ('idle' if not open_flags else ''),
            },
            {
                'num': member_counts['active'],
                'label': 'Active members',
                'url': _changelist('member', status__exact='active'),
                'state': '',
            },
            {
                'num': member_counts['prospects'],
                'label': 'Prospects',
                'url': _changelist('member', status__exact='prospect'),
                'state': '',
            },
            {
                'num': recent_errors,
                'label': 'Agent errors (7d)',
                'url': _changelist('tasklog', level__exact='error'),
                'state': 'attention' if recent_errors else 'good',
            },
        ],
        'flags': (
            AdminFlag.objects
            .filter(is_resolved=False)
            .select_related('member')
            .order_by('-created_at')[:12]
        ),
        'agents': agents,
        'agents_unconfigured': not configs,
        'upcoming_events': (
            Event.objects
            .filter(is_published=True, date__gte=today)
            .select_related('chamber')
            .order_by('date')[:5]
        ),
        'open_circles': IronCircle.objects.filter(is_open=True).count(),
        'flag_changelist': _changelist('adminflag', is_resolved__exact=0),
        'agent_changelist': _changelist('agentconfig'),
        'event_changelist': _changelist('event'),
    }


@register.filter
def priority_rank(flags):
    """Sort flags urgent -> high -> medium -> low for display."""
    order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
    return sorted(flags, key=lambda f: (order.get(f.priority, 9), -f.id))
