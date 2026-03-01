"""
Social Media Agent
==================

Auto-generates social captions from blog posts and manages post scheduling.

Schedule: When BlogPost published + 3x weekly content check
Phase: 4 (stub ready for implementation)
"""

from crm.agents import is_agent_active, log_task, update_agent_run

AGENT_NAME = 'social_media'


def generate_post_from_blog(blog_post_id):
    """Generate social media captions from a newly published blog post."""
    from crm.models import BlogPost, SocialMediaPost

    if not is_agent_active(AGENT_NAME):
        return

    try:
        post = BlogPost.objects.get(id=blog_post_id)
    except BlogPost.DoesNotExist:
        return

    platforms = ['instagram', 'tiktok', 'youtube']
    created = 0

    for platform in platforms:
        # Check if post already exists for this blog + platform
        exists = SocialMediaPost.objects.filter(
            blog_post=post, platform=platform
        ).exists()

        if not exists:
            # Generate a caption from the blog excerpt or content
            excerpt = post.excerpt or post.content[:200]
            caption = (
                f"{post.title}\n\n"
                f"{excerpt}\n\n"
                f"Keep climbing, brother.\n\n"
                f"#TheChamberofMen #MenOfFaith #IronCircle #KeepClimbing"
            )

            SocialMediaPost.objects.create(
                platform=platform,
                caption=caption,
                hashtags='#TheChamberofMen #MenOfFaith #IronCircle #KeepClimbing',
                blog_post=post,
                status='draft',
            )
            created += 1

    if created:
        log_task(
            AGENT_NAME, f'Generated {created} social posts from blog',
            f'Blog: {post.title}', level='success'
        )
        update_agent_run(AGENT_NAME)


def weekly_content_check():
    """Check for unpublished social posts and flag for review."""
    from crm.models import SocialMediaPost

    if not is_agent_active(AGENT_NAME):
        return

    drafts = SocialMediaPost.objects.filter(status='draft').count()

    if drafts > 0:
        log_task(
            AGENT_NAME, f'{drafts} social media posts awaiting review',
            'Check the Social Media Posts section in admin.', level='info'
        )

    update_agent_run(AGENT_NAME)
