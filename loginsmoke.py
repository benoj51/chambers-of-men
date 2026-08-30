import os, django, traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE','chambers.settings'); django.setup()
from django.conf import settings as S
S.ALLOWED_HOSTS.append('testserver')
from django.test import Client
from django.contrib.auth import get_user_model
U=get_user_model()
U.objects.filter(username='ben').delete()
U.objects.create_superuser('ben','b@e.com','chambers-dev-pw-1')

c=Client(enforce_csrf_checks=True)
print("1. GET /admin/login/ ...")
r=c.get('/admin/login/')
print("   ->", r.status_code)
tok=r.cookies.get('csrftoken')
csrf=tok.value if tok else r.context['csrf_token'] if r.context else ''
print("2. POST credentials ...")
try:
    r2=c.post('/admin/login/',{'username':'ben','password':'chambers-dev-pw-1','csrfmiddlewaretoken':csrf,'next':'/admin/'})
    print("   ->", r2.status_code, "redirect:", r2.get('Location'))
    if r2.status_code in (301,302):
        r3=c.get(r2['Location'])
        print("3. GET", r2['Location'], "->", r3.status_code)
except Exception as e:
    print("   CRASH:", type(e).__name__, e); traceback.print_exc()
