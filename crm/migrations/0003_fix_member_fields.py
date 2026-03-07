from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_agentconfig_emailtemplate_and_more'),
    ]

    operations = [
        # Rename fields to match updated models.py
        migrations.RenameField(
            model_name='member',
            old_name='onboarding_status',
            new_name='onboarding_step',
        ),
        migrations.RenameField(
            model_name='member',
            old_name='interview_scheduled_date',
            new_name='interview_date',
        ),
        migrations.RenameField(
            model_name='member',
            old_name='last_engagement_date',
            new_name='last_activity_date',
        ),
        # Update field types to match models.py
        migrations.AlterField(
            model_name='member',
            name='onboarding_step',
            field=models.CharField(max_length=50, default='new', blank=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='interview_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='last_activity_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        # Add new fields
        migrations.AddField(
            model_name='member',
            name='onboarding_started',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='member',
            name='engagement_score',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
