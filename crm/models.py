from django.db import models
from django.utils import timezone


class Chamber(models.Model):
    """A local or regional Chamber - the organisational unit of the movement."""
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    chamber_lead = models.ForeignKey(
        'Member', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='led_chambers'
    )
    parent_chamber = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sub_chambers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.city}"

    class Meta:
        ordering = ['name']


class Member(models.Model):
    """A member or prospect of Chambers of Men."""
    STATUS_CHOICES = [
        ('prospect', 'Prospect'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    ROLE_CHOICES = [
        ('member', 'Member'),
        ('foundation_support', 'Foundation Support'),
        ('iron_circle_leader', 'Iron Circle Leader'),
        ('media_expert', 'Media & Social Media Expert'),
        ('admin_pm', 'Admin & Project Manager'),
        ('chamber_lead', 'Chamber Lead'),
        ('elder', 'Elder'),
    ]

    HOW_HEARD_CHOICES = [
        ('social_media', 'Social Media'),
        ('church', 'Church'),
        ('friend', 'Friend / Word of Mouth'),
        ('event', 'Event'),
        ('website', 'Website'),
        ('other', 'Other'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='prospect')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='member')
    how_heard = models.CharField(max_length=20, choices=HOW_HEARD_CHOICES, blank=True)

    chamber = models.ForeignKey(
        Chamber, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='members'
    )

    date_joined = models.DateField(default=timezone.now)
    church_membership_years = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="How many years the member has been active in their church"
    )
    notes = models.TextField(blank=True)
    reason_for_joining = models.TextField(blank=True, help_text="Why they want to be part of Chambers of Men")

    # Agent framework fields
    onboarding_step = models.CharField(max_length=50, default='new', blank=True)
    onboarding_started = models.DateTimeField(null=True, blank=True)
    interview_date = models.DateField(null=True, blank=True)
    last_activity_date = models.DateTimeField(null=True, blank=True)
    engagement_score = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['-created_at']


class IronCircle(models.Model):
    """An Iron Circle - a small group of 3-5 men meeting weekly."""
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    name = models.CharField(max_length=200)
    circle_leader = models.ForeignKey(
        Member, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='led_circles'
    )
    chamber = models.ForeignKey(
        Chamber, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='circles'
    )
    members = models.ManyToManyField(Member, blank=True, related_name='circles')
    meeting_day = models.CharField(max_length=10, choices=DAY_CHOICES, blank=True)
    meeting_time = models.TimeField(null=True, blank=True)
    meeting_location = models.CharField(max_length=200, blank=True)
    is_open = models.BooleanField(default=True, help_text="Whether the circle is accepting new members")
    max_members = models.PositiveIntegerField(default=5)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()

    @property
    def is_full(self):
        return self.members.count() >= self.max_members

    class Meta:
        ordering = ['name']


class Event(models.Model):
    """Events within the movement."""
    TYPE_CHOICES = [
        ('men_reborn', 'Men Reborn (Launch)'),
        ('man_at_altar', 'Man at the Altar (Monthly Prayer)'),
        ('leadership_summit', 'Leadership Summit (Bi-Annual)'),
        ('gathering', 'Gathering of the Chambers (Annual)'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    chamber = models.ForeignKey(
        Chamber, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='events'
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.date}"

    class Meta:
        ordering = ['-date']


class EventAttendance(models.Model):
    """Track member attendance at events."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendance_records')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='event_attendance')
    attended = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.member} - {self.event}"

    class Meta:
        unique_together = ['event', 'member']


class BlogPost(models.Model):
    """Blog posts / content for the website."""
    CATEGORY_CHOICES = [
        ('doctrine', 'Chamber Doctrine'),
        ('testimony', 'Testimony'),
        ('devotional', 'Devotional'),
        ('update', 'Movement Update'),
        ('teaching', 'Teaching'),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True, max_length=500)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='teaching')
    author = models.ForeignKey(
        Member, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='blog_posts'
    )
    featured_image = models.ImageField(upload_to='blog/', blank=True)
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_published and not self.published_date:
            self.published_date = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-published_date']


class ContactSubmission(models.Model):
    """Contact form submissions from the website."""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)
    how_heard = models.CharField(max_length=100, blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email} ({self.created_at.strftime('%d/%m/%Y')})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Signup / Contact Submission'
        verbose_name_plural = 'Signup / Contact Submissions'


# ============================================================
# Agent Framework Models
# ============================================================

class AgentConfig(models.Model):
    """Configuration for each automated agent."""
    agent_name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    last_run = models.DateTimeField(null=True, blank=True)
    run_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = 'Active' if self.is_active else 'Paused'
        return f"{self.agent_name} ({status})"

    class Meta:
        ordering = ['agent_name']
        verbose_name = 'Agent Configuration'


class EmailTemplate(models.Model):
    """Reusable email templates for agent communications."""
    template_key = models.CharField(max_length=100, unique=True)
    subject = models.CharField(
        max_length=300,
        help_text="Email subject line. Use {{ name }} for personalisation."
    )
    body_html = models.TextField(
        help_text=(
            "HTML email body. Available variables: {{ name }}, {{ first_name }}, "
            "{{ email }}, {{ city }}, {{ event_name }}, {{ event_date }}, "
            "{{ circle_name }}, {{ leader_name }}, {{ interview_date }}"
        )
    )
    body_text = models.TextField(
        blank=True,
        help_text="Plain text fallback. Leave blank to auto-generate from the HTML."
    )
    from_name = models.CharField(max_length=100, blank=True)
    from_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True, help_text="Enable/disable this template")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.template_key}: {self.subject}"

    def render(self, context_data=None):
        """Render subject, HTML body and text body against ``context_data``.

        Returns a ``(subject, body_html, body_text)`` tuple. ``body_text`` is
        returned as stored; the caller is responsible for deriving a fallback
        when it is blank.
        """
        from django.template import Context, Template

        ctx = Context(context_data or {})
        subject = Template(self.subject).render(ctx)
        body_html = Template(self.body_html).render(ctx)
        body_text = Template(self.body_text).render(ctx) if self.body_text else ''
        return subject, body_html, body_text

    @property
    def sender(self):
        """Full ``Name <email>`` sender string, falling back to project defaults."""
        from django.conf import settings

        name = self.from_name or getattr(settings, 'DEFAULT_FROM_NAME', '')
        email = self.from_email or settings.DEFAULT_FROM_EMAIL
        return f"{name} <{email}>" if name else email

    class Meta:
        ordering = ['template_key']


class TaskLog(models.Model):
    """Log of all agent task executions."""
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
    ]

    agent_name = models.CharField(max_length=50, help_text="Which agent performed this action")
    task_name = models.CharField(max_length=200, help_text="What the agent did")
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='info')
    message = models.TextField(blank=True, help_text="Additional details or error messages")
    details = models.JSONField(
        default=dict, blank=True,
        help_text="Structured context, e.g. email_sent_to / template_used"
    )
    member = models.ForeignKey(
        Member, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='task_logs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.agent_name}] {self.task_name} - {self.level}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task Log'


class MemberActivityLog(models.Model):
    """Track member activities for engagement scoring."""
    ACTIVITY_TYPES = [
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
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    points = models.PositiveIntegerField(
        default=1, help_text="Weighting used by the engagement score"
    )
    related_event = models.ForeignKey(
        Event, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='activity_logs'
    )
    related_circle = models.ForeignKey(
        IronCircle, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='activity_logs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member} - {self.activity_type} ({self.created_at.strftime('%d/%m/%Y')})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Member Activity Log'


class AdminFlag(models.Model):
    """Flags raised by agents for admin attention."""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    FLAG_TYPE_CHOICES = [
        ('inactive_member', 'Inactive Member'),
        ('circle_capacity', 'Circle at Capacity'),
        ('low_event_rsvp', 'Low Event RSVP'),
        ('missing_data', 'Missing Member Data'),
        ('onboarding_stalled', 'Onboarding Stalled'),
        ('leadership_candidate', 'Leadership Candidate'),
        ('general', 'General Alert'),
    ]

    agent_name = models.CharField(max_length=50, help_text="Which agent raised this flag")
    flag_type = models.CharField(
        max_length=30, choices=FLAG_TYPE_CHOICES, default='general',
        help_text="Used to de-duplicate repeat flags for the same member"
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    member = models.ForeignKey(
        Member, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='admin_flags'
    )
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.CharField(max_length=200, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = 'Resolved' if self.is_resolved else 'Open'
        return f"[{self.priority.upper()}] {self.title} ({status})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Admin Flag'


class SocialMediaPost(models.Model):
    """Scheduled social media posts."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ]

    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('youtube', 'YouTube'),
        ('twitter', 'Twitter / X'),
    ]

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    content = models.TextField(help_text="Post caption / description")
    hashtags = models.TextField(blank=True, help_text="Hashtags separated by spaces")
    media_url = models.URLField(blank=True)
    blog_post = models.ForeignKey(
        BlogPost, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='social_posts', help_text="Blog post this was generated from"
    )
    scheduled_for = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    external_id = models.CharField(
        max_length=200, blank=True, help_text="ID from the platform after publishing"
    )
    engagement_data = models.JSONField(
        default=dict, blank=True, help_text="Likes, shares, comments, views"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform} - {self.status} - {self.content[:50]}"

    class Meta:
        ordering = ['-scheduled_for']
        verbose_name = 'Social Media Post'


class CircleAssignmentHistory(models.Model):
    """History of Iron Circle assignments for tracking."""
    ACTION_CHOICES = [
        ('joined', 'Joined Circle'),
        ('left', 'Left Circle'),
        ('transferred', 'Transferred'),
        ('promoted_leader', 'Promoted to Leader'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='circle_history')
    circle = models.ForeignKey(IronCircle, on_delete=models.CASCADE, related_name='assignment_history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='joined')
    assigned_date = models.DateField(default=timezone.now)
    removed_date = models.DateField(null=True, blank=True)
    reason = models.TextField(blank=True)
    performed_by = models.CharField(
        max_length=200, blank=True, help_text="Agent or admin who made the change"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member} -> {self.circle} ({self.assigned_date})"

    class Meta:
        ordering = ['-assigned_date']
        verbose_name = 'Circle Assignment History'
        verbose_name_plural = 'Circle Assignment Histories'


class LeadershipProgression(models.Model):
    """Track leadership pipeline progression."""
    STATUS_CHOICES = [
        ('nominated', 'Nominated'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='leadership_progressions'
    )
    from_role = models.CharField(max_length=30, choices=Member.ROLE_CHOICES)
    to_role = models.CharField(max_length=30, choices=Member.ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='nominated')
    nominated_by = models.CharField(
        max_length=200, default='system', help_text="Agent or leader who recommended"
    )
    reviewed_by = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True, help_text="Why this progression was recommended or made")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_pending(self):
        return self.status in ('nominated', 'under_review')

    def __str__(self):
        return f"{self.member}: {self.from_role} -> {self.to_role} ({self.status})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Leadership Progression'
