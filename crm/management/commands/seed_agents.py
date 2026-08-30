"""
Management command to seed default AgentConfig and EmailTemplate records.

Usage:
    python manage.py seed_agents
    python manage.py seed_agents --update   # overwrite existing template copy

The previous version of this file was truncated mid-way through the template
list and the remainder overwritten with binary data, which made the whole
command unimportable. It has been rebuilt: the eleven templates below match the
keys the agent modules actually request, and all of them now use the v2 brand
palette (the surviving four were still on the retired v1 teal).
"""

from django.core.management.base import BaseCommand

from crm.models import AgentConfig, EmailTemplate

# --- v2 brand tokens (see BRAND_v2.md §3) ----------------------------------
BG_DEEP = '#0B0F14'      # members-club ground
TERRACOTTA = '#D17F56'   # primary accent
CREAM = '#EFE9DB'        # reading colour on dark
PAPER = '#E8DFCC'        # warm paper for the inverted body panel

HEADING_FONT = "Newsreader, Georgia, 'Times New Roman', serif"
BODY_FONT = "'DM Sans', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def shell(body, footer_line='You are not alone, brother.'):
    """Wrap a template body in the shared Chambers of Men email chrome."""
    return f'''<div style="font-family: {BODY_FONT}; max-width: 600px; margin: 0 auto; padding: 20px; line-height: 1.7;">
    <div style="background: {BG_DEEP}; padding: 30px; text-align: center;">
        <h1 style="font-family: {HEADING_FONT}; color: {TERRACOTTA}; margin: 0; font-size: 28px;">Chambers of Men</h1>
        <p style="color: {CREAM}; margin: 10px 0 0; font-style: italic;">Awaken. Equip. Deploy.</p>
    </div>

    <div style="padding: 30px; background: {PAPER}; color: {BG_DEEP};">
{body}
    </div>

    <div style="background: {BG_DEEP}; padding: 15px; text-align: center;">
        <p style="color: {CREAM}; margin: 0; font-size: 12px;">{footer_line}</p>
    </div>
</div>'''


SIGN_OFF = '''        <p style="margin-top: 30px;"><strong>Keep climbing, brother.</strong></p>

        <p>Benedict<br>Chambers of Men</p>'''


class Command(BaseCommand):
    help = 'Seed default agent configurations and email templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Overwrite the subject and body of templates that already exist.',
        )

    def handle(self, *args, **options):
        self._seed_agent_configs()
        self._seed_email_templates(update=options['update'])
        self.stdout.write(self.style.SUCCESS('Agent framework seeded successfully.'))

    def _seed_agent_configs(self):
        agents = [
            {
                'agent_name': 'onboarding',
                'is_active': True,
                'config': {
                    'welcome_delay_minutes': 0,
                    'follow_up_days': [2, 5, 10],
                    'stalled_grace_days': 7,
                },
            },
            {
                'agent_name': 'crm_pipeline',
                'is_active': True,
                'config': {
                    'inactive_threshold_days': 90,
                },
            },
            {
                'agent_name': 'event_manager',
                'is_active': True,
                'config': {
                    'reminder_days': [7, 1],
                },
            },
            {
                'agent_name': 'iron_circle',
                'is_active': True,
                'config': {
                    'max_circle_size': 5,
                    'match_by_city': True,
                },
            },
            {
                'agent_name': 'social_media',
                'is_active': False,  # Off by default until the publishing API is configured
                'config': {
                    'platforms': ['instagram', 'tiktok', 'youtube'],
                },
            },
            {
                'agent_name': 'leadership',
                'is_active': True,
                'config': {
                    'min_activities_for_promotion': 5,
                    'min_events_for_promotion': 2,
                },
            },
        ]

        for agent_data in agents:
            obj, created = AgentConfig.objects.get_or_create(
                agent_name=agent_data['agent_name'],
                defaults={
                    'is_active': agent_data['is_active'],
                    'config': agent_data['config'],
                }
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f"  {status}: {obj}")

    def _seed_email_templates(self, update=False):
        templates = [
            {
                'template_key': 'welcome',
                'subject': 'Welcome to Chambers of Men, {{ first_name }}',
                'body_html': shell(f'''        <p>Hi {{{{ first_name }}}},</p>

        <p>Thank you for your interest in joining Chambers of Men. We are honoured that you have taken this step.</p>

        <p>Chambers of Men is a movement dedicated to restoring men to the image of God through structured leadership, doctrinal purity, and strategic deployment. We are building something real - a brotherhood that sharpens, supports, and sends.</p>

        <p>Here is what happens next:</p>

        <ol>
            <li>A member of our team will review your details</li>
            <li>We will reach out to schedule a brief introductory conversation</li>
            <li>You will be matched with an Iron Circle - a small group of 3 to 5 men who meet weekly</li>
        </ol>

        <p>In the meantime, reply to this email with any questions.</p>

{SIGN_OFF}''', footer_line='You are not alone, brother.'),
            },
            {
                'template_key': 'follow_up_day_2',
                'subject': '{{ first_name }}, a question about your walk',
                'body_html': shell(f'''        <p>Hi {{{{ first_name }}}},</p>

        <p>A couple of days ago you registered your interest in Chambers of Men. Before we speak, it helps to know where you are starting from.</p>

        <p>Two questions, and short answers are fine:</p>

        <ol>
            <li>Where are you in your walk with God right now?</li>
            <li>What made you reach out when you did?</li>
        </ol>

        <p>There are no wrong answers here. Men come into the Chambers from every kind of season - some steady, some barely holding on. Both belong.</p>

{SIGN_OFF}''', footer_line='You are not alone, brother.'),
            },
            {
                'template_key': 'follow_up_day_5',
                'subject': 'What an Iron Circle actually looks like',
                'body_html': shell(f'''        <p>Hi {{{{ first_name }}}},</p>

        <p>An Iron Circle is three to five men who meet weekly. That is it. No stage, no audience, no performance.</p>

        <p>What happens in that room:</p>

        <ul>
            <li><strong>Accountability</strong> - real questions, honestly answered</li>
            <li><strong>Scripture</strong> - worked through together, not lectured</li>
            <li><strong>Prayer</strong> - for each other, by name, every week</li>
        </ul>

        <p>"As iron sharpens iron, so one man sharpens another." (Proverbs 27:17)</p>

        <p>If you would like to take the next step, reply and we will arrange a short introductory call.</p>

{SIGN_OFF}''', footer_line='You are not alone, brother.'),
            },
            {
                'template_key': 'follow_up_day_10',
                'subject': 'The door stays open, {{ first_name }}',
                'body_html': shell(f'''        <p>Hi {{{{ first_name }}}},</p>

        <p>We have not heard back, and that is completely fine. Life gets busy, and timing matters.</p>

        <p>If now is not the right season, the door remains open whenever you are ready. If you are still interested, simply reply to this email and we will pick it up from there.</p>

        <p>Until then, we will keep you in our prayers.</p>

{SIGN_OFF}''', footer_line='You are not alone, brother.'),
            },
            {
                'template_key': 'interview_reminder',
                'subject': 'Tomorrow: your introductory conversation',
                'body_html': shell(f'''        <p>Hi {{{{ first_name }}}},</p>

        <p>A reminder that your introductory conversation with Chambers of Men is scheduled for <strong>{{{{ interview_date }}}}</strong>.</p>

        <p>It is a relaxed conversation, usually 15 to 30 minutes. We want to get to know you, hear your story, and answer anything you want to ask about the movement or the Iron Circles.</p>

        <p>If you need to reschedule, reply to this email and we will sort it out.</p>

{SIGN_OFF}''', footer_line='You are not alone, brother.'),
            },
            {
                'template_key': 'event_reminder_7d',
                'subject': '{{ event_name }} is next week',
                'body_html': shell(f'''        <p>Hi {{{{ first_name }}}},</p>

        <p>A heads up - <strong>{{{{ event_name }}}}</strong> is happening on <strong>{{{{ event_date }}}}</strong> at {{{{ event_location }}}}.</p>

        <p>Mark your calendar and come ready to stand shoulder to shoulder with your brothers.</p>

{SIGN_OFF}''', footer_line='Keep climbing, brother.'),
            },
            {
                'template_key': 'event_reminder_1d',
                'subject': 'Tomorrow: {{ event_name }}',
                'body_html': shell(f'''        <p>Hi {{{{ first_name }}}},</p>

        <p>Quick reminder - <strong>{{{{ event_name }}}}</strong> is <strong>tomorrow</strong>, {{{{ event_date }}}} at {{{{ event_location }}}}.</p>

        <p>We are looking forward to seeing you there.</p>

{SIGN_OFF}''', footer_line='Keep climbing, brother.'),
            },
            {
                'template_key': 'event_thank_you',
                'subject': 'Thank you for standing with us at {{ event_name }}',
                'body_html': shell(f'''        <p>Hi {{{{ first_name }}}},</p>

        <p>Thank you for being at <strong>{{{{ event_name }}}}</strong>.</p>

        <p>What was stirred in that room is not meant to stay there. Take one thing you heard and put it into practice this week - in your home, your work, your walk.</p>

{SIGN_OFF}''', footer_line='Keep climbing, brother.'),
            },
            {
                'template_key': 'circle_welcome',
                'subject': 'You have been matched: {{ circle_name }}',
                'body_html': shell(f'''        <p>Hi {{{{ first_name }}}},</p>

        <p>You have been matched to <strong>{{{{ circle_name }}}}</strong>.</p>

        <p>Your circle leader is <strong>{{{{ leader_name }}}}</strong>, who will be in touch with the meeting time and place.</p>

        <p>Come as you are. The only thing asked of you is that you show up honestly and keep showing up.</p>

{SIGN_OFF}''', footer_line='You are not alone, brother.'),
            },
            {
                'template_key': 'circle_meeting_reminder',
                'subject': '{{ circle_name }} meets this week',
                'body_html': shell(f'''        <p>Hi {{{{ first_name }}}},</p>

        <p>Your circle, <strong>{{{{ circle_name }}}}</strong>, meets this week.</p>

        <p>Your brothers are expecting you. If you cannot make it, let {{{{ leader_name }}}} know rather than going quiet.</p>

{SIGN_OFF}''', footer_line='You are not alone, brother.'),
            },
            {
                'template_key': 'inactive_warning',
                'subject': 'We have missed you, {{ first_name }}',
                'body_html': shell(f'''        <p>Hi {{{{ first_name }}}},</p>

        <p>It has been a while since we saw you, and we noticed. Life pulls us into many directions, and we understand that.</p>

        <p>But we want you to know your brothers have not forgotten about you. Chambers of Men is here whenever you are ready to re-engage.</p>

        <p>If there is something going on that we can support you with, or if you would like to step back for a season, simply reply to this email. No pressure, no judgement - just brothers.</p>

{SIGN_OFF}''', footer_line='You are not alone, brother.'),
            },
        ]

        for tmpl_data in templates:
            obj, created = EmailTemplate.objects.get_or_create(
                template_key=tmpl_data['template_key'],
                defaults={
                    'subject': tmpl_data['subject'],
                    'body_html': tmpl_data['body_html'],
                },
            )
            if created:
                status = 'Created'
            elif update:
                obj.subject = tmpl_data['subject']
                obj.body_html = tmpl_data['body_html']
                obj.save(update_fields=['subject', 'body_html', 'updated_at'])
                status = 'Updated'
            else:
                status = 'Already exists (use --update to refresh)'
            self.stdout.write(f"  {status}: {obj.template_key}")
