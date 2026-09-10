from django.contrib import admin, messages
from django.utils.html import format_html
from .models import (
    Chamber, Member, IronCircle, Event,
    EventAttendance, BlogPost, ContactSubmission,
    AgentConfig, EmailTemplate, TaskLog,
    MemberActivityLog, AdminFlag, SocialMediaPost,
    CircleAssignmentHistory, LeadershipProgression,
)
















# ---------------------------------------------------------------------------
# Existing CRM Admin
# ---------------------------------------------------------------------------








@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [
        'first_name', 'last_name', 'email', 'status', 'role',
        'onboarding_step', 'city', 'date_joined'
    ]
    list_filter = ['status', 'role', 'onboarding_step', 'how_heard', 'chamber']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'city']
    list_select_related = ['chamber']
    date_hierarchy = 'date_joined'
    list_editable = ['status', 'role']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'city', 'address')
        }),
        ('Membership', {
            'fields': ('status', 'role', 'chamber', 'date_joined', 'how_heard', 'church_membership_years')
        }),
        ('Onboarding & Engagement', {
            'fields': ('onboarding_step', 'interview_date', 'last_activity_date'),
            'description': 'Managed by the Onboarding and CRM Pipeline agents.'
        }),
        ('Additional', {
            'fields': ('reason_for_joining', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
















@admin.register(Chamber)
class ChamberAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'region', 'chamber_lead', 'member_count']
    search_fields = ['name', 'city']
    list_filter = ['region']
    list_select_related = ['chamber_lead']

    @admin.display(description='Members')
    def member_count(self, obj):
        return obj.members.count()
















class CircleMemberInline(admin.TabularInline):
    model = IronCircle.members.through
    extra = 1
















@admin.register(IronCircle)
class IronCircleAdmin(admin.ModelAdmin):
    list_display = ['name', 'circle_leader', 'chamber', 'meeting_day', 'member_count', 'is_open']
    list_filter = ['is_open', 'meeting_day', 'chamber']
    search_fields = ['name']
    list_select_related = ['circle_leader', 'chamber']
    inlines = [CircleMemberInline]
    exclude = ['members']








    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'
















class EventAttendanceInline(admin.TabularInline):
    model = EventAttendance
    extra = 1
















@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_type', 'date', 'location', 'is_published']
    list_filter = ['event_type', 'is_published', 'chamber']
    list_select_related = ['chamber']
    date_hierarchy = 'date'
    search_fields = ['name', 'location']
    list_editable = ['is_published']
    inlines = [EventAttendanceInline]
















@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_published', 'published_date']
    list_filter = ['is_published', 'category']
    list_select_related = ['author']
    search_fields = ['title', 'content']
    list_editable = ['is_published']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
















@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'city', 'is_processed', 'created_at']
    list_filter = ['is_processed', 'how_heard']
    search_fields = ['name', 'email']
    list_editable = ['is_processed']
    readonly_fields = ['created_at']








    actions = ['mark_as_processed', 'create_member_from_submission', 'run_onboarding']

    @admin.display(description="Mark selected as processed")
    def mark_as_processed(self, request, queryset):
        updated = queryset.update(is_processed=True)
        self.message_user(request, f"{updated} submission(s) marked as processed.")

    @admin.display(description="Create member records (no email sent)")
    def create_member_from_submission(self, request, queryset):
        from crm.agents.onboarding import _map_how_heard

        created = skipped = 0
        for sub in queryset:
            name_parts = sub.name.strip().split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            if Member.objects.filter(email=sub.email).exists():
                skipped += 1
            else:
                Member.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=sub.email,
                    phone=sub.phone,
                    city=sub.city,
                    reason_for_joining=sub.message,
                    # how_heard is free text on the form but a choice on Member;
                    # reuse the agent's mapping rather than dropping the value.
                    how_heard=_map_how_heard(sub.how_heard),
                    status='prospect',
                )
                created += 1
            sub.is_processed = True
            sub.save(update_fields=['is_processed'])

        msg = f"{created} member(s) created."
        if skipped:
            msg += f" {skipped} skipped - a member with that email already exists."
        self.message_user(request, msg)

    @admin.display(description="Run onboarding (create member + send welcome email)")
    def run_onboarding(self, request, queryset):
        """Delegate to the onboarding agent instead of duplicating its logic.

        The agent creates the Member, sends the welcome email and marks the
        submission processed. It is a no-op while the agent is paused, so say
        so rather than reporting a success that did not happen.
        """
        from crm.agents import is_agent_active
        from crm.agents.onboarding import process_new_signup

        if not is_agent_active('onboarding'):
            self.message_user(
                request,
                "The onboarding agent is paused - nothing was sent. "
                "Enable it under Agent Configurations first.",
                level=messages.WARNING,
            )
            return

        processed = failed = 0
        for sub in queryset:
            try:
                process_new_signup(sub.id)
                processed += 1
            except Exception as exc:
                failed += 1
                self.message_user(
                    request, f"{sub.email}: {type(exc).__name__}: {exc}",
                    level=messages.ERROR,
                )
        if processed:
            self.message_user(
                request,
                f"Onboarding run for {processed} submission(s). "
                f"See Task Logs for exactly what was sent.",
            )
        if failed:
            self.message_user(
                request, f"{failed} submission(s) failed.", level=messages.ERROR)
















# ---------------------------------------------------------------------------
# Agent Framework Admin
# ---------------------------------------------------------------------------








@admin.register(AgentConfig)
class AgentConfigAdmin(admin.ModelAdmin):
    list_display = ['agent_name', 'is_active', 'last_run', 'run_count', 'updated_at']
    readonly_fields = ['last_run', 'run_count', 'created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('agent_name', 'is_active')
        }),
        ('Configuration', {
            'fields': ('config',),
            'description': 'Agent-specific settings in JSON format. Leave as {} for defaults.'
        }),
        ('Run Statistics', {
            'fields': ('last_run', 'run_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
















@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['template_key', 'subject', 'updated_at']
    search_fields = ['subject', 'body_html']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('template_key',)
        }),
        ('Content', {
            'fields': ('subject', 'body_html'),
            'description': (
                'Use Django template variables: {{ name }}, {{ first_name }}, '
                '{{ email }}, {{ city }}, {{ event_name }}, {{ event_date }}, '
                '{{ circle_name }}, {{ leader_name }}, {{ interview_date }}'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
















@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'agent_name', 'task_name', 'level_badge', 'member']
    list_filter = ['agent_name', 'level', 'created_at']
    list_select_related = ['member']
    search_fields = ['task_name', 'message']
    readonly_fields = [
        'agent_name', 'task_name', 'message', 'level', 'member',
        'details', 'created_at'
    ]
    date_hierarchy = 'created_at'








    def level_badge(self, obj):
        colours = {
            'info': '#3B82F6',
            'success': '#10B981',
            'warning': '#F59E0B',
            'error': '#EF4444',
        }
        colour = colours.get(obj.level, '#6B7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            colour, obj.get_level_display()
        )
    level_badge.short_description = 'Level'








    def has_add_permission(self, request):
        return False








    def has_change_permission(self, request, obj=None):
        return False
















@admin.register(MemberActivityLog)
class MemberActivityLogAdmin(admin.ModelAdmin):
    list_display = ['member', 'activity_type', 'points', 'description', 'created_at']
    list_filter = ['activity_type', 'created_at']
    list_select_related = ['member']
    search_fields = ['member__first_name', 'member__last_name', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
















@admin.register(AdminFlag)
class AdminFlagAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority_badge', 'flag_type', 'agent_name', 'member', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'priority', 'flag_type', 'agent_name']
    list_select_related = ['member']
    date_hierarchy = 'created_at'
    search_fields = ['title', 'description', 'member__first_name', 'member__last_name']
    list_editable = ['is_resolved']
    readonly_fields = ['created_at']
    actions = ['resolve_flags']








    def priority_badge(self, obj):
        colours = {
            'low': '#6B7280',
            'medium': '#F59E0B',
            'high': '#F97316',
            'urgent': '#EF4444',
        }
        colour = colours.get(obj.priority, '#6B7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            colour, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'








    def resolve_flags(self, request, queryset):
        from django.utils import timezone
        queryset.update(
            is_resolved=True,
            resolved_by=request.user.username,
            resolved_at=timezone.now(),
        )
        self.message_user(request, f"{queryset.count()} flag(s) resolved.")
    resolve_flags.short_description = "Resolve selected flags"
















@admin.register(SocialMediaPost)
class SocialMediaPostAdmin(admin.ModelAdmin):
    list_display = ['platform', 'caption_preview', 'status', 'scheduled_for', 'blog_post']
    list_filter = ['platform', 'status', 'scheduled_for']
    search_fields = ['content', 'hashtags']
    list_editable = ['status']
    list_select_related = ['blog_post']
    readonly_fields = ['created_at', 'published_at', 'external_id', 'engagement_data']








    def caption_preview(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    caption_preview.short_description = 'Content'
















@admin.register(CircleAssignmentHistory)
class CircleAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ['member', 'circle', 'action', 'assigned_date', 'removed_date', 'performed_by']
    list_filter = ['action', 'assigned_date']
    list_select_related = ['member', 'circle']
    search_fields = ['member__first_name', 'member__last_name', 'circle__name']
    readonly_fields = ['assigned_date']
















@admin.register(LeadershipProgression)
class LeadershipProgressionAdmin(admin.ModelAdmin):
    list_display = ['member', 'from_role', 'to_role', 'status', 'nominated_by', 'created_at']
    list_filter = ['status', 'to_role']
    list_select_related = ['member']
    search_fields = ['member__first_name', 'member__last_name']
    list_editable = ['status']
    readonly_fields = ['created_at']
    actions = ['approve_progressions']








    def approve_progressions(self, request, queryset):
        # 'pending' is not one of STATUS_CHOICES - this used to match nothing
        # and still report success. The reviewable states are nominated and
        # under_review.
        from django.utils import timezone

        approved = 0
        for progression in queryset.filter(status__in=('nominated', 'under_review')):
            progression.status = 'approved'
            progression.reviewed_by = request.user.username
            progression.reviewed_at = timezone.now()
            progression.save()
            member = progression.member
            member.role = progression.to_role
            member.save(update_fields=['role', 'updated_at'])
            approved += 1

        skipped = queryset.count() - approved
        msg = f"{approved} progression(s) approved and member roles updated."
        if skipped:
            msg += f" {skipped} skipped - already approved or declined."
        self.message_user(request, msg)
    approve_progressions.short_description = "Approve selected and update member roles"
















# Customise the admin site header
admin.site.site_header = "Chambers of Men - CRM"
admin.site.site_title = "Chambers of Men"
admin.site.index_title = "Dashboard"




















