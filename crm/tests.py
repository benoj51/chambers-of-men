"""Regression tests for the CRM and the agent framework.

Every test here pins a failure that was live in production:

* Five admin list pages returned a 500 because models.py described columns the
  database did not have (``test_every_admin_page_loads``,
  ``test_no_model_migration_drift``).
* Every agent module raised on its first ORM call because it was written
  against the pre-0003 field names (``AgentTaskTests``).
* ``seed_agents.py`` was unimportable - the file had been truncated and the
  remainder overwritten with binary data (``test_all_management_commands_import``).
* Agents requested email templates that were never seeded
  (``test_every_template_the_agents_request_is_seeded``).
"""

from datetime import timedelta
from importlib import import_module
from io import StringIO
from pkgutil import iter_modules

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.questioner import NonInteractiveMigrationQuestioner
from django.db.migrations.state import ProjectState
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from crm import models as crm_models
from crm.models import (
    AdminFlag, AgentConfig, BlogPost, Chamber, ContactSubmission, EmailTemplate,
    Event, EventAttendance, IronCircle, LeadershipProgression, Member,
    MemberActivityLog, SocialMediaPost, TaskLog,
)

SYNC_Q = {'sync': True, 'timeout': 30, 'orm': 'default'}


class MigrationIntegrityTests(TestCase):
    """The root cause: models.py and the migrations described different tables."""

    def test_no_model_migration_drift(self):
        loader = MigrationLoader(None, ignore_no_migrations=True)
        autodetector = MigrationAutodetector(
            loader.project_state(),
            ProjectState.from_apps(__import__('django.apps', fromlist=['apps']).apps),
            NonInteractiveMigrationQuestioner(specified_apps=set(), dry_run=True),
        )
        changes = autodetector.changes(graph=loader.graph)
        self.assertEqual(
            changes, {},
            "Models have drifted from migrations - run makemigrations. "
            "This drift is what made five admin pages return a 500.",
        )


class ManagementCommandTests(TestCase):

    def test_all_management_commands_import(self):
        """A corrupted seed_agents.py went unnoticed because nothing imported it."""
        import crm.management.commands as pkg

        failures = []
        for mod in iter_modules(pkg.__path__):
            try:
                import_module(f'crm.management.commands.{mod.name}')
            except Exception as exc:  # pragma: no cover - failure path
                failures.append(f'{mod.name}: {type(exc).__name__}: {exc}')
        self.assertEqual(failures, [], f'Unimportable management commands: {failures}')

    def test_seed_agents_is_idempotent(self):
        call_command('seed_agents', verbosity=0, stdout=StringIO())
        first = (AgentConfig.objects.count(), EmailTemplate.objects.count())
        call_command('seed_agents', verbosity=0, stdout=StringIO())
        self.assertEqual(first, (AgentConfig.objects.count(), EmailTemplate.objects.count()))

    def test_every_template_the_agents_request_is_seeded(self):
        import re
        from pathlib import Path

        call_command('seed_agents', verbosity=0, stdout=StringIO())
        agents_dir = Path(__file__).resolve().parent / 'agents'
        requested = set()
        for path in agents_dir.glob('*.py'):
            requested |= set(
                re.findall(r"send_template_email\(\s*'([^']+)'", path.read_text())
            )
        seeded = set(EmailTemplate.objects.values_list('template_key', flat=True))
        self.assertEqual(
            requested - seeded, set(),
            'Agents request email templates that seed_agents does not create.',
        )

    def test_setup_schedules_registers_every_agent_task(self):
        from django_q.models import Schedule

        call_command('setup_schedules', verbosity=0, stdout=StringIO())
        funcs = set(Schedule.objects.values_list('func', flat=True))
        self.assertTrue(funcs, 'No schedules were registered')
        for func in funcs:
            module_path, func_name = func.rsplit('.', 1)
            module = import_module(module_path)
            self.assertTrue(
                callable(getattr(module, func_name, None)),
                f'Scheduled task {func} does not resolve to a callable',
            )


class AdminSmokeTests(TestCase):
    """Every registered admin page must load - this is the CRM's only UI."""

    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_superuser('admin', 'a@e.com', 'pw-for-tests-123')
        chamber = Chamber.objects.create(name='London Chamber', city='London')
        member = Member.objects.create(
            first_name='Test', last_name='Man', email='t@e.com',
            city='London', status='active', chamber=chamber,
        )
        circle = IronCircle.objects.create(name='London A', chamber=chamber)
        event = Event.objects.create(
            name='Men Reborn', event_type='men_reborn',
            date=timezone.now().date(), is_published=True,
        )
        # One row in every table so list pages render real columns, not an
        # empty queryset that would hide a bad column reference.
        EventAttendance.objects.create(event=event, member=member, attended=True)
        BlogPost.objects.create(title='T', slug='t', content='c', is_published=True)
        ContactSubmission.objects.create(name='N', email='n@e.com')
        AgentConfig.objects.create(agent_name='onboarding')
        EmailTemplate.objects.create(template_key='k', subject='s', body_html='<p>b</p>')
        TaskLog.objects.create(agent_name='onboarding', task_name='t', message='m')
        MemberActivityLog.objects.create(member=member, activity_type='circle_meeting')
        AdminFlag.objects.create(agent_name='onboarding', flag_type='general', title='t')
        SocialMediaPost.objects.create(platform='instagram', content='c')
        crm_models.CircleAssignmentHistory.objects.create(member=member, circle=circle)
        LeadershipProgression.objects.create(
            member=member, from_role='member', to_role='elder')

    def setUp(self):
        self.client.force_login(get_user_model().objects.get(username='admin'))

    def test_every_admin_page_loads(self):
        from django.contrib import admin

        request = self.client.request().wsgi_request
        request.user = get_user_model().objects.get(username='admin')

        failures = []
        for model, model_admin in admin.site._registry.items():
            opts = model._meta
            views = [f'admin:{opts.app_label}_{opts.model_name}_changelist']
            # Read-only log tables (TaskLog, django-q's queues) deliberately
            # deny add, and correctly return 403 - do not treat that as broken.
            if model_admin.has_add_permission(request):
                views.append(f'admin:{opts.app_label}_{opts.model_name}_add')

            for viewname in views:
                url = reverse(viewname)
                try:
                    response = self.client.get(url)
                    if response.status_code != 200:
                        failures.append(f'{url} -> HTTP {response.status_code}')
                except Exception as exc:
                    failures.append(f'{url} -> {type(exc).__name__}: {exc}')
        self.assertEqual(failures, [], f'Broken admin pages: {failures}')

    def test_every_admin_change_page_loads(self):
        """The changelist can pass while the change form references a bad field."""
        from django.contrib import admin

        failures = []
        for model in admin.site._registry:
            instance = model.objects.first()
            if instance is None:
                continue
            opts = model._meta
            url = reverse(
                f'admin:{opts.app_label}_{opts.model_name}_change', args=[instance.pk])
            try:
                response = self.client.get(url)
                if response.status_code != 200:
                    failures.append(f'{url} -> HTTP {response.status_code}')
            except Exception as exc:
                failures.append(f'{url} -> {type(exc).__name__}: {exc}')
        self.assertEqual(failures, [], f'Broken admin change pages: {failures}')


class PublicSiteTests(TestCase):

    def test_public_pages_load(self):
        for name in ('home', 'about', 'events', 'blog_list', 'contact', 'styleguide'):
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    @override_settings(Q_CLUSTER=SYNC_Q)
    def test_signup_creates_a_submission(self):
        response = self.client.post(reverse('signup'), {
            'name': 'John Smith', 'email': 'john@example.com',
            'city': 'London', 'how_heard': 'church',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ContactSubmission.objects.filter(email='john@example.com').exists())

    @override_settings(Q_CLUSTER=SYNC_Q)
    def test_signup_rejects_missing_email(self):
        self.client.post(reverse('signup'), {'name': 'No Email'})
        self.assertFalse(ContactSubmission.objects.filter(name='No Email').exists())

    @override_settings(Q_CLUSTER=SYNC_Q)
    def test_signup_json_response(self):
        response = self.client.post(
            reverse('signup'),
            {'name': 'Ajax Man', 'email': 'ajax@example.com'},
            headers={'accept': 'application/json'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    Q_CLUSTER=SYNC_Q,
)
class AgentTaskTests(TestCase):
    """Each agent task must complete against the real schema.

    Before the 0004 migration every one of these raised on its first query.
    """

    def setUp(self):
        call_command('seed_agents', verbosity=0, stdout=StringIO())
        AgentConfig.objects.update(is_active=True)
        self.now = timezone.now()
        self.chamber = Chamber.objects.create(name='London Chamber', city='London')
        self.circle = IronCircle.objects.create(
            name='London A', chamber=self.chamber, is_open=True, max_members=5)

    def _member(self, email, **kwargs):
        kwargs.setdefault('first_name', 'A')
        kwargs.setdefault('last_name', 'B')
        kwargs.setdefault('city', 'London')
        return Member.objects.create(email=email, **kwargs)

    def test_new_signup_creates_member_and_sends_welcome(self):
        from crm.agents.onboarding import process_new_signup

        sub = ContactSubmission.objects.create(
            name='John Smith', email='john@example.com', city='London', how_heard='church')
        process_new_signup(sub.id)

        member = Member.objects.get(email='john@example.com')
        self.assertEqual(member.first_name, 'John')
        self.assertEqual(member.onboarding_step, 'welcome_sent')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('John', mail.outbox[0].subject)
        self.assertTrue(ContactSubmission.objects.get(pk=sub.pk).is_processed)

    def test_task_log_records_email_metadata_in_details(self):
        from crm.agents import log_task

        log_task('onboarding', 'Welcome sent', 'to John', level='success',
                 email_sent_to='john@example.com', template_used='welcome')
        log = TaskLog.objects.get()
        self.assertEqual(log.task_name, 'Welcome sent')
        self.assertEqual(log.details['email_sent_to'], 'john@example.com')
        self.assertEqual(log.details['template_used'], 'welcome')

    def test_follow_up_sequence_advances_each_stage(self):
        from crm.agents.onboarding import process_follow_ups

        stages = [
            ('welcome_sent', 3, 'follow_up_1'),
            ('follow_up_1', 6, 'follow_up_2'),
            ('follow_up_2', 11, 'follow_up_3'),
        ]
        for i, (start, age_days, expected) in enumerate(stages):
            member = self._member(f's{i}@e.com', onboarding_step=start)
            Member.objects.filter(pk=member.pk).update(
                created_at=self.now - timedelta(days=age_days))

        process_follow_ups()

        for i, (_, _, expected) in enumerate(stages):
            self.assertEqual(
                Member.objects.get(email=f's{i}@e.com').onboarding_step, expected)

    def test_interview_reminder_matches_on_date_not_datetime(self):
        """interview_date became a DateField in 0003; the agent still used a
        datetime range, so reminders never matched."""
        from crm.agents.onboarding import process_follow_ups

        self._member(
            'interview@e.com', onboarding_step='interview_scheduled',
            interview_date=(self.now + timedelta(days=1)).date(),
        )
        process_follow_ups()
        self.assertTrue(
            any('interview@e.com' in m.to for m in mail.outbox),
            'No interview reminder was sent for an interview scheduled tomorrow',
        )

    def test_pipeline_flags_inactive_and_unassigned_members(self):
        from crm.agents.crm_pipeline import daily_pipeline_check

        self._member('stale@e.com', status='active', chamber=self.chamber,
                     last_activity_date=self.now - timedelta(days=200))
        self._member('nochamber@e.com', status='active')
        daily_pipeline_check()

        types = set(AdminFlag.objects.values_list('flag_type', flat=True))
        self.assertIn('inactive_member', types)
        self.assertIn('missing_data', types)

    def test_admin_flags_are_not_duplicated_across_runs(self):
        from crm.agents.crm_pipeline import daily_pipeline_check

        self._member('stale@e.com', status='active', chamber=self.chamber,
                     last_activity_date=self.now - timedelta(days=200))
        daily_pipeline_check()
        count = AdminFlag.objects.count()
        daily_pipeline_check()
        daily_pipeline_check()
        self.assertEqual(AdminFlag.objects.count(), count,
                         'Daily agents raised duplicate flags on re-run')

    def test_event_reminders_render_the_member_name(self):
        """A stray space in the context key ({' name'}) left {{ name }} blank."""
        from crm.agents.event_manager import daily_event_check

        self._member('goer@e.com', first_name='Marcus', status='active')
        Event.objects.create(
            name='Man at the Altar', event_type='man_at_altar',
            date=(self.now + timedelta(days=1)).date(),
            is_published=True, location='London',
        )
        daily_event_check()
        self.assertTrue(mail.outbox, 'No event reminder was sent')
        self.assertNotIn('{{', mail.outbox[0].body)

    def test_circle_matching_assigns_and_records_history(self):
        from crm.agents.iron_circle import match_member_to_circle

        member = self._member('seeker@e.com', status='active')
        match_member_to_circle(member.id)

        self.assertIn(member, self.circle.members.all())
        history = crm_models.CircleAssignmentHistory.objects.get(member=member)
        self.assertEqual(history.action, 'joined')
        self.assertEqual(history.performed_by, 'Iron Circle Agent')

    def test_circle_matching_flags_when_no_circle_available(self):
        from crm.agents.iron_circle import match_member_to_circle

        IronCircle.objects.update(is_open=False)
        member = self._member('unmatched@e.com', status='active')
        match_member_to_circle(member.id)
        self.assertTrue(
            AdminFlag.objects.filter(flag_type='circle_capacity').exists())

    def test_leadership_nominates_engaged_members(self):
        from crm.agents.leadership import quarterly_review

        member = self._member('rising@e.com', status='active', role='member')
        for _ in range(6):
            MemberActivityLog.objects.create(member=member, activity_type='circle_meeting')
        for i in range(2):
            event = Event.objects.create(
                name=f'E{i}', event_type='other', date=self.now.date())
            EventAttendance.objects.create(event=event, member=member, attended=True)

        quarterly_review()
        progression = LeadershipProgression.objects.get(member=member)
        self.assertEqual(progression.status, 'nominated')
        self.assertEqual(progression.to_role, 'foundation_support')

        quarterly_review()
        self.assertEqual(LeadershipProgression.objects.filter(member=member).count(), 1)

    def test_social_media_generates_one_draft_per_platform(self):
        from crm.agents.social_media import generate_post_from_blog

        post = BlogPost.objects.create(
            title='On Brotherhood', slug='on-brotherhood',
            content='Iron sharpens iron. ' * 30, is_published=True,
        )
        generate_post_from_blog(post.id)
        self.assertEqual(SocialMediaPost.objects.filter(blog_post=post).count(), 3)

        generate_post_from_blog(post.id)
        self.assertEqual(SocialMediaPost.objects.filter(blog_post=post).count(), 3)

    def test_paused_agents_do_not_run(self):
        from crm.agents.onboarding import process_new_signup

        AgentConfig.objects.filter(agent_name='onboarding').update(is_active=False)
        sub = ContactSubmission.objects.create(name='Nope', email='nope@e.com')
        process_new_signup(sub.id)
        self.assertFalse(Member.objects.filter(email='nope@e.com').exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_every_scheduled_task_runs_without_error(self):
        """Catch-all: run each cron entry point against an empty-ish database."""
        from crm.agents import (
            crm_pipeline, event_manager, iron_circle, leadership, onboarding,
            social_media,
        )

        tasks = [
            onboarding.process_follow_ups,
            crm_pipeline.daily_pipeline_check,
            event_manager.daily_event_check,
            iron_circle.monthly_circle_review,
            social_media.weekly_content_check,
            leadership.quarterly_review,
        ]
        for task in tasks:
            with self.subTest(task=task.__name__):
                task()
