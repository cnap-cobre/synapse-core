from importlib import import_module
import inspect

def get_refresh_token_url(app):
    views = import_module('allauth.socialaccount.providers.' + app + '.views')
    for name, obj in inspect.getmembers(views):
        if inspect.isclass(obj) and 'Adapter' in name \
                and app.upper() in  name.upper():
            return obj.access_token_url


def get_protected_url(app):
    views = import_module('allauth.socialaccount.providers.' + app + '.views')
    for name, obj in inspect.getmembers(views):
        if inspect.isclass(obj) and 'Adapter' in name \
                and app.upper() in  name.upper():
            return obj.profile_url

