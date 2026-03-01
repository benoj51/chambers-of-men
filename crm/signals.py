"""
Django signal handlers for the agent framework.

These connect model events (post_save, etc.) to agent actions,
providing real-time triggers without polling.

In production (with qcluster running), tasks are queued asynchronously.
In development (no worker), tasks run synchronously via Django-Q's sync mode
or direct function calls.
"""

import logging
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger('chambers.agents')


def _run_agent_task(func_path, *args, task_name='', group=''):
    """
    Run an agent task - async via Django-Q in production, sync in development.
    """
    if settings.DEBUG:
        # In development, run synchronously for immediate feedback
        module_path, func_name = func_path.rsplit('.', 1)
        import importlib
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)
        func(*args)
        return

    try:
        from django_q.tasks import async_task
        async_task(func_path, *args, task_name=task_name, group=group)
        logger.info(f"Queued task: {task_name}")
    except Exception as e:
        # Fallback to synchronous if queue fails
        logger.warning(f"Queue failed for {task_name}, running sync: {e}")
        module_path, func_name = func_path.rsplit('.', 1)
        import importlib
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)
        func(*args)


@receiver(post_save, sender='crm.ContactSubmission')
def on_new_signup(sender, instance, created, **kwargs):
    """When a new ContactSubmission is created, trigger the Onboarding Agent."""
    if not created:
        return

    _run_agent_task(
        'crm.agents.onboarding.process_new_signup',
        instance.id,
        task_name=f'onboarding-welcome-{instance.id}',
        group='onboarding',
    )


@receiver(post_save, sender='crm.BlogPost')
def on_blog_published(sender, instance, **kwargs):
    """When a blog post is published, trigger social media post generation."""
    if not instance.is_published:
        return

    _run_agent_task(
        'crm.agents.social_media.generate_post_from_blog',
        instance.id,
        task_name=f'social-media-blog-{instance.id}',
        group='social_media',
    )
