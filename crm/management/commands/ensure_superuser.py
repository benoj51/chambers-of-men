import os
import sys
import traceback
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create or update a superuser from environment variables'

    def handle(self, *args, **options):
        try:
            sys.stderr.write('[ensure_superuser] Starting...\n')
            User = get_user_model()
            username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
            email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'benojuolape@gmail.com')
            password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')

            sys.stderr.write('[ensure_superuser] Username: ' + username + '\n')
            sys.stderr.write('[ensure_superuser] Password length: ' + str(len(password)) + '\n')

            if not password:
                sys.stderr.write('[ensure_superuser] WARNING: No password set\n')
                return

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'is_staff': True,
                    'is_superuser': True,
                }
            )

            if created:
                user.set_password(password)
                user.save()
                sys.stderr.write('[ensure_superuser] Created superuser\n')
            else:
                user.set_password(password)
                user.email = email
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save()
                sys.stderr.write('[ensure_superuser] Updated superuser\n')

            # Verify password works
            from django.contrib.auth import authenticate
            test_user = authenticate(username=username, password=password)
            if test_user is not None:
                sys.stderr.write('[ensure_superuser] VERIFIED: Auth works\n')
            else:
                sys.stderr.write('[ensure_superuser] FAILED: Auth test failed\n')
                check_user = User.objects.get(username=username)
                sys.stderr.write('[ensure_superuser] is_active=' + str(check_user.is_active) + '\n')
                sys.stderr.write('[ensure_superuser] has_usable_pw=' + str(check_user.has_usable_password()) + '\n')

        except Exception as e:
            sys.stderr.write('[ensure_superuser] ERROR: ' + str(e) + '\n')
            sys.stderr.write(traceback.format_exc())
