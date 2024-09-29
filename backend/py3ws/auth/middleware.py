from re import compile

from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

from py3ws.utils.utils import is_ajax

if not hasattr(settings, 'LOGIN_URL'):
    raise Exception('Brak zdefiniowanego URL dla strony logowania')

EXEMPT_URLS = []

if hasattr(settings, 'EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.EXEMPT_URLS]


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).
    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    """

    def process_request(self, request):
        assert hasattr(request, 'user'), \
            "The Login Required middleware\
            requires authentication middleware to be installed. Edit your\
            MIDDLEWARE_CLASSES setting to insert\
            'django.contrib.auth.middleware.AuthenticationMiddleware'. If that doesn't\
            work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
            'django.core.context_processors.auth'."

        path = request.path_info.lstrip('/')

        if not request.user.is_authenticated:
            if not any(m.match(path) for m in EXEMPT_URLS):
                if is_ajax(request):
                    return JsonResponse(
                        {'errmsg': 'Sesja użytkownika %s wygasła. Proszę się ponownie zalogować' % request.user.username},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                return HttpResponseRedirect(settings.LOGIN_URL)
        else:
            if not request.user.is_active:
                return redirect('user.inactive')
            if not request.user.password_valid:
                if '/%s' % path != reverse('user.changepassword'):
                    return redirect('user.changepassword')
