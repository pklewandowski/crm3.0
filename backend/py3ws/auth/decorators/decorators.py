import six
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test


def p3permission_required(perm, login_url=None, raise_exception=True, errmsg=None):
    def check_perms(user):
        if isinstance(perm, six.string_types):
            perms = (perm, )
        else:
            perms = perm
        if user.has_perms(perms):
            return True
        if raise_exception and user.pk:
            raise PermissionDenied(errmsg)
        return False

    return user_passes_test(check_perms, login_url=login_url)