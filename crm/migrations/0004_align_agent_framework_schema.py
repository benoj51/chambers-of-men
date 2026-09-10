"""Realign the agent-framework tables with crm/models.py.

Migrations 0002/0003 left seven tables describing a different schema from the
one models.py declares. The admin queried columns the database did not have,
so five CRM list pages returned a 500, and every agent module wrote to columns
that no longer existed.

Renames are used wherever a column carries the same meaning under a new name so
that existing rows survive. TaskLog's two email audit columns are folded into
the new ``details`` JSON field before being dropped.
"""

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def fold_email_audit_into_details(apps, schema_editor):
    """Preserve TaskLog.email_sent_to / template_used inside details."""
    TaskLog = apps.get_model('crm', 'TaskLog')
    for log in TaskLog.objects.exclude(email_sent_to='', template_used='').iterator():
        details = log.details if isinstance(log.details, dict) else {}
        if log.email_sent_to:
            details.setdefault('email_sent_to', log.email_sent_to)
        if log.template_used:
            details.setdefault('template_used', log.template_used)
        log.details = details
        log.save(update_fields=['details'])


def unfold_email_audit_from_details(apps, schema_editor):
    TaskLog = apps.get_model('crm', 'TaskLog')
    for log in TaskLog.objects.iterator():
        details = log.details if isinstance(log.details, dict) else {}
        log.email_sent_to = details.get('email_sent_to', '') or ''
        log.template_used = details.get('template_used', '') or ''
        log.save(update_fields=['email_sent_to', 'template_used'])


def approved_flag_to_status(apps, schema_editor):
    """is_approved was a boolean; status is a four-state field."""
    LP = apps.get_model('crm', 'LeadershipProgression')
    LP.objects.filter(is_approved=True).update(status='approved')
    LP.objects.filter(is_approved=False).update(status='nominated')


def status_to_approved_flag(apps, schema_editor):
    LP = apps.get_model('crm', 'LeadershipProgression')
    LP.objects.update(is_approved=False)
    LP.objects.filter(status='approved').update(is_approved=True)


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_fix_member_fields'),
    ]

    operations = [
        # ------------------------------------------------------------------
        # TaskLog: action -> task_name, detail -> message, + details JSON
        # ------------------------------------------------------------------
        migrations.RenameField('tasklog', old_name='action', new_name='task_name'),
        migrations.RenameField('tasklog', old_name='detail', new_name='message'),
        migrations.AddField(
            model_name='tasklog',
            name='details',
            field=models.JSONField(
                blank=True, default=dict,
                help_text='Structured context, e.g. email_sent_to / template_used',
            ),
        ),
        migrations.RunPython(fold_email_audit_into_details, unfold_email_audit_from_details),
        migrations.RemoveField(model_name='tasklog', name='email_sent_to'),
        migrations.RemoveField(model_name='tasklog', name='template_used'),
        migrations.AlterField(
            model_name='tasklog',
            name='agent_name',
            field=models.CharField(help_text='Which agent performed this action', max_length=50),
        ),
        migrations.AlterField(
            model_name='tasklog',
            name='task_name',
            field=models.CharField(help_text='What the agent did', max_length=200),
        ),
        migrations.AlterField(
            model_name='tasklog',
            name='message',
            field=models.TextField(blank=True, help_text='Additional details or error messages'),
        ),
        migrations.AlterField(
            model_name='tasklog',
            name='level',
            field=models.CharField(
                choices=[('info', 'Info'), ('warning', 'Warning'),
                         ('error', 'Error'), ('success', 'Success')],
                default='info', max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name='tasklog',
            name='member',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='task_logs', to='crm.member',
            ),
        ),
        migrations.AlterModelOptions(
            name='tasklog',
            options={'ordering': ['-created_at'], 'verbose_name': 'Task Log'},
        ),

        # ------------------------------------------------------------------
        # MemberActivityLog: + points, widen the activity vocabulary
        # ------------------------------------------------------------------
        migrations.AddField(
            model_name='memberactivitylog',
            name='points',
            field=models.PositiveIntegerField(
                default=1, help_text='Weighting used by the engagement score'),
        ),
        migrations.AlterField(
            model_name='memberactivitylog',
            name='activity_type',
            field=models.CharField(
                choices=[
                    ('event_attendance', 'Event Attendance'),
                    ('circle_meeting', 'Circle Meeting'),
                    ('leadership_task', 'Leadership Task'),
                    ('mentoring', 'Mentoring Session'),
                    ('outreach', 'Outreach Activity'),
                    ('email_opened', 'Email Opened'),
                    ('email_clicked', 'Email Link Clicked'),
                    ('form_submission', 'Form Submission'),
                    ('interview_completed', 'Interview Completed'),
                    ('role_assigned', 'Role Assigned'),
                    ('other', 'Other'),
                ],
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name='memberactivitylog',
            name='related_event',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='activity_logs', to='crm.event',
            ),
        ),
        migrations.AlterField(
            model_name='memberactivitylog',
            name='related_circle',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='activity_logs', to='crm.ironcircle',
            ),
        ),
        migrations.AlterModelOptions(
            name='memberactivitylog',
            options={'ordering': ['-created_at'], 'verbose_name': 'Member Activity Log'},
        ),

        # ------------------------------------------------------------------
        # AdminFlag
        # ------------------------------------------------------------------
        migrations.AlterField(
            model_name='adminflag',
            name='agent_name',
            field=models.CharField(help_text='Which agent raised this flag', max_length=50),
        ),
        migrations.AlterField(
            model_name='adminflag',
            name='flag_type',
            field=models.CharField(
                choices=[
                    ('inactive_member', 'Inactive Member'),
                    ('circle_capacity', 'Circle at Capacity'),
                    ('low_event_rsvp', 'Low Event RSVP'),
                    ('missing_data', 'Missing Member Data'),
                    ('onboarding_stalled', 'Onboarding Stalled'),
                    ('leadership_candidate', 'Leadership Candidate'),
                    ('general', 'General Alert'),
                ],
                default='general',
                help_text='Used to de-duplicate repeat flags for the same member',
                max_length=30,
            ),
        ),
        migrations.AlterModelOptions(
            name='adminflag',
            options={'ordering': ['-created_at'], 'verbose_name': 'Admin Flag'},
        ),

        # ------------------------------------------------------------------
        # SocialMediaPost: caption -> content, external_post_id -> external_id
        # ------------------------------------------------------------------
        migrations.RenameField('socialmediapost', old_name='caption', new_name='content'),
        migrations.RenameField(
            'socialmediapost', old_name='external_post_id', new_name='external_id'),
        migrations.AddField(
            model_name='socialmediapost',
            name='media_url',
            field=models.URLField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='socialmediapost',
            name='content',
            field=models.TextField(help_text='Post caption / description'),
        ),
        migrations.AlterField(
            model_name='socialmediapost',
            name='platform',
            field=models.CharField(
                choices=[('instagram', 'Instagram'), ('tiktok', 'TikTok'),
                         ('youtube', 'YouTube'), ('twitter', 'Twitter / X')],
                max_length=20,
            ),
        ),
        migrations.AlterModelOptions(
            name='socialmediapost',
            options={'ordering': ['-scheduled_for'], 'verbose_name': 'Social Media Post'},
        ),

        # ------------------------------------------------------------------
        # CircleAssignmentHistory: + assigned_date / removed_date
        # ------------------------------------------------------------------
        migrations.AddField(
            model_name='circleassignmenthistory',
            name='assigned_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='circleassignmenthistory',
            name='removed_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='circleassignmenthistory',
            name='action',
            field=models.CharField(
                choices=[('joined', 'Joined Circle'), ('left', 'Left Circle'),
                         ('transferred', 'Transferred'),
                         ('promoted_leader', 'Promoted to Leader')],
                default='joined', max_length=20,
            ),
        ),
        migrations.AlterModelOptions(
            name='circleassignmenthistory',
            options={
                'ordering': ['-assigned_date'],
                'verbose_name': 'Circle Assignment History',
                'verbose_name_plural': 'Circle Assignment Histories',
            },
        ),

        # ------------------------------------------------------------------
        # LeadershipProgression: is_approved -> status, plus renames
        # ------------------------------------------------------------------
        migrations.RenameField(
            'leadershipprogression', old_name='recommended_by', new_name='nominated_by'),
        migrations.RenameField(
            'leadershipprogression', old_name='reason', new_name='notes'),
        migrations.RenameField(
            'leadershipprogression', old_name='approved_by', new_name='reviewed_by'),
        migrations.RenameField(
            'leadershipprogression', old_name='approved_at', new_name='reviewed_at'),
        migrations.AddField(
            model_name='leadershipprogression',
            name='status',
            field=models.CharField(
                choices=[('nominated', 'Nominated'), ('under_review', 'Under Review'),
                         ('approved', 'Approved'), ('declined', 'Declined')],
                default='nominated', max_length=20,
            ),
        ),
        migrations.RunPython(approved_flag_to_status, status_to_approved_flag),
        migrations.RemoveField(model_name='leadershipprogression', name='is_approved'),
        migrations.AlterField(
            model_name='leadershipprogression',
            name='nominated_by',
            field=models.CharField(
                default='system', help_text='Agent or leader who recommended', max_length=200),
        ),
        migrations.AlterField(
            model_name='leadershipprogression',
            name='notes',
            field=models.TextField(
                blank=True, help_text='Why this progression was recommended or made'),
        ),
        migrations.AlterField(
            model_name='leadershipprogression',
            name='member',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='leadership_progressions', to='crm.member',
            ),
        ),
        migrations.AlterModelOptions(
            name='leadershipprogression',
            options={'ordering': ['-created_at'], 'verbose_name': 'Leadership Progression'},
        ),

        # ------------------------------------------------------------------
        # EmailTemplate / AgentConfig: drop the hard-coded key vocabularies so
        # new templates and agents can be added without a migration.
        # ------------------------------------------------------------------
        migrations.AlterField(
            model_name='emailtemplate',
            name='template_key',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='emailtemplate',
            name='from_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='emailtemplate',
            name='from_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='emailtemplate',
            name='body_text',
            field=models.TextField(
                blank=True,
                help_text='Plain text fallback. Leave blank to auto-generate from the HTML.'),
        ),
        migrations.AlterModelOptions(
            name='emailtemplate',
            options={'ordering': ['template_key']},
        ),
        migrations.AlterField(
            model_name='agentconfig',
            name='agent_name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='agentconfig',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='agentconfig',
            name='config',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterModelOptions(
            name='agentconfig',
            options={'ordering': ['agent_name'], 'verbose_name': 'Agent Configuration'},
        ),
    ]
