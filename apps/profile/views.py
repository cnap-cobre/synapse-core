from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

import hashlib
import datetime

@login_required
def add_beocat_script(request, template_name='add_beocat_script.html'):
    session_key = request.COOKIES[settings.SESSION_COOKIE_NAME]
    csrf = request.COOKIES['csrftoken']
    return render(request, template_name, {
        'sessionkey': session_key,
        'csrftoken': csrf,
        'hash': hashlib.sha224(str(datetime.datetime.now()).encode('utf-8')).hexdigest()[0:6]
    }, content_type='text/plain')
