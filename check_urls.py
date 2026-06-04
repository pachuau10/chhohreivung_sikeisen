import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'sikeisen.settings'
sys.path.insert(0, 'E:\\Django project\\Sikeisen')
import django
django.setup()
from django.urls import reverse
names = ['account_reset_password', 'account_reset_password_done', 'account_reset_password_from_key', 'account_reset_password_from_key_done']
for n in names:
    if n == 'account_reset_password_from_key':
        print(f'{n}: {reverse(n, kwargs={"uidb36":"abc","key":"xyz"})}')
    else:
        print(f'{n}: {reverse(n)}')
os.remove(__file__)
