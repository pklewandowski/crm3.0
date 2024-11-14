import datetime
import os

from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR, 'ver')) as f:
    VERSION = f.read() # '3.0.0'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ.get('CRM_DEBUG') else False



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@@4yeno6ur(otlw&4d^wkk4ie)_957t@c1s51qknnno4u$qxdv'

ALLOWED_HOSTS = ['localhost']
INTERNAL_IPS = ['localhost', '127.0.0.']

# Application definition

INSTALLED_APPS = [
    'django_crontab',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'apps.address',
    'apps.app_settings',
    'apps.attachment',
    'apps.attribute',
    'apps.company',
    'apps.config',
    'apps.dict',
    'apps.document.apps.DocumentConfig',
    'apps.file_repository',
    'apps.financial_accounting.batch_processing',
    'apps.financial_accounting.invoice',
    'apps.financial_accounting.transaction',
    'apps.gus',
    'apps.hierarchy',
    'apps.home',
    'apps.log',
    'apps.login',
    'apps.marketing.lp',
    'apps.marketing.partner',
    'apps.meeting_room',
    'apps.message',
    'apps.note',
    'apps.notification',
    'apps.ocr',
    'apps.product_retail',
    'apps.product',
    'apps.report',
    'apps.schedule_app.apps.ScheduleAppConfig',
    'apps.scheduler.schedule',
    'apps.stat.summary_report',
    'apps.tag',
    'apps.user_func.adviser',
    'apps.user_func.broker',
    'apps.user_func.client',
    'apps.user_func.contractor',
    'apps.user_func.employee',
    'apps.user.apps.UserConfig',
    'apps.widget',
    'apps.email.email_client.apps.EmailClientConfig',
    'apps.table_report.apps.TableReportConfig',
    'rest_framework',
    'utils',
    # ---- external 3rd party libs ---- #
    # 'debug_toolbar',
    'mptt',
    'mathfilters',
    'nolastlogin',
    'py3ws',
    'simple_history',
    # ---- temporary ---- #
    '_temp'
]

MIDDLEWARE = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'py3ws.auth.middleware.LoginRequiredMiddleware',
    'py3ws.middleware.log.userActions.UserActionLogger',
    # 'py3ws.middleware.error.error_handler.ErrorHandlerMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'apps.product_retail.middleware.ProductRetailMiddleware'
]

ATTACHMENT_ROOT_RELATIVE = 'document/attachments'
# ATTACHMENT_ROOT = os.path.join(MEDIA_ROOT, ATTACHMENT_ROOT_RELATIVE)
#
# AVATAR_ROOT = os.path.join(MEDIA_ROOT, 'avatar')

ROOT_URLCONF = 'crm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            (os.path.join(BASE_DIR, 'templates')),
            (os.path.join(BASE_DIR, 'application/templates'))
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'apps.notification.context_processors.get_notifications',
                'apps.config.context_processors.get_cookies',
                'apps.config.context_processors.get_default_encoding'
            ],
            'builtins': ['py3ws.template.tags.tags'],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # 'django.db.backends.sqlite3',
        'OPTIONS': {
            'options': '-c search_path=crm'
        },
        'NAME': os.getenv('DBNAME'),
        'USER': os.getenv('DBUSER'),
        'PASSWORD': os.getenv('DBPASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'DATABASE_SCHEMA': os.getenv('DBSCHEMA'),
        'TEST':
            {
                'ENGINE': 'django.db.backends.postgresql',
                'OPTIONS': {
                    'options': '-c search_path=crm'
                },
                'NAME': 'test_crm',
                'USER': 'test_crm',
                'PASSWORD': 'test_crm',
                'HOST': '127.0.0.1',
                'PORT': '5432',
                'DATABASE_SCHEMA': 'crm'
            }
        # 'ATOMIC_REQUESTS': True, # automatyczne założenie transakcji przed uruchomieniem porcedury obsługi requestu (viewsa - czyli inaczej kontrolera)
    },
}

DATABASE_SCHEMA = 'crm'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'user.User'
MODEL_PERMS_LIST = (
    ('app_permissions_hierarchy', 'hierarchy', 'hierarchy', _('Struktura firmy')),
    ('app_permissions_user', 'user', 'user', _('Użytkownicy i grupy')),
    ('app_permissions_client', 'client', 'client', _('Klienci')),
    ('app_permissions_adviser', 'adviser', 'adviser', _('Doradcy')),
    ('app_permissions_broker', 'broker', 'broker', _('Pośrednicy')),
    ('app_permissions_document', 'document', 'document', _('Dokumenty')),
    ('app_permissions_documenttype', 'document', 'documenttype', _('Typy dokumentów')),
    ('app_permissions_product', 'product', 'product', _('Produkty')),
    ('app_permissions_attribute', 'attribute', 'attribute', _('Atrybuty')),
    ('app_permissions_attachment', 'attachment', 'attachment', _('Załączniki')),
    ('app_permissions_meeting_room', 'meeting_room', 'meetingroom', _('Biuro')),
    ('app_permissions_schedule', 'schedule', 'schedule', _('Kalendarz')),
    ('app_permissions_dict', 'dict', 'dictionary', _('Słowniki')),
    ('app_permissions_dictentry', 'dict', 'dictionaryentry', _('Wpisy słowników')),
    ('app_permissions_partner', 'partner', 'partnerlead', _('Partner Lead')),
)

# DEBUG_TOOLBAR_PANELS = [
#     'debug_toolbar.panels.versions.VersionsPanel',
#     'debug_toolbar.panels.timer.TimerPanel',
#     'debug_toolbar.panels.settings.SettingsPanel',
#     'debug_toolbar.panels.headers.HeadersPanel',
#     'debug_toolbar.panels.request.RequestPanel',
#     'debug_toolbar.panels.sql.SQLPanel',
#     'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#     'debug_toolbar.panels.templates.TemplatesPanel',
#     'debug_toolbar.panels.cache.CachePanel',
#     'debug_toolbar.panels.signals.SignalsPanel',
#     'debug_toolbar.panels.logging.LoggingPanel',
#     'debug_toolbar.panels.redirects.RedirectsPanel',
# ]

# DEBUG_TOOLBAR_CONFIG = {
#     'INTERCEPT_REDIRECTS': False,
# }

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
LOCALE_NAME = 'pl_PL'
LANGUAGE_CODE = 'pl'

TIME_ZONE = 'Europe/Warsaw'

USE_I18N = True
USE_L10N = False
USE_TZ = False

FORMAT_MODULE_PATH = [
    'crm.formats',
]

DATETIME_FORMAT = 'Y-m-d H:i:s'
DATE_FORMAT = '%Y-%m-%d'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "../_staticBuild"),
]

STATIC_ROOT = os.path.join(BASE_DIR + "/../", 'static')
STATIC_URL = '/static/'

SESSION_COOKIE_AGE = 60 * 60
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = (
    'google.com',
    'googleapis.com',
)

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

LOGIN_URL = '/login/'

EXEMPT_URLS = (
    r'^about\.html$',
    r'^legal/',  # allow any URL under /legal/*
    r'^user/inactive/',
    r'^user/api/reset-password/',
    r'^client/complete/',
    r'^schedule/schedule-participant-confirm-from-link/',
    r'^login/',
    r'^logout/',
    r'^marketing/partner/add/'
)

MODE_CREATE = 'C'
MODE_EDIT = 'E'
MODE_VIEW = 'V'
MODE_DELETE = 'D'
MODE_FILTER = 'F'
DICTIONARY_CLASS = 'apps.dict.models.DictionaryEntry'

USER_TYPE_CLIENT = 'cli'
USER_TYPE_ADVISER = 'adv'
USER_TYPE_BROKER = 'brk'
USER_TYPE_EMPLOYEE = 'emp'

FORM_FIELD_BASE_CSS_CLASS = 'form-control input-md'
FORM_FIELD_ERROR_CSS_CLASS = 'form-field-error'
FORM_FIELD_REQUIRED_CSS_CLASS = 'form-field-required'

GENERIC_DATATYPES = (
    ('string', 'tekst'),
    ('text', 'tekst długi'),
    ('decimal', 'liczba'),
    ('date', 'data'),
    ('datetime', 'data i czas'),
    ('time', 'czas'),
)

IFRAME_BASE_TEMPLATE = 'iframe.html'
CLIENT_HAS_BROKER = True

SCHEDULE_WORKING_HOURS = {'start': datetime.time(11), 'end': datetime.time(22)}
SCHEDULE_WORKING_DAYS = [1, 2, 3, 4, 5]
SCHEDULE_EVENT_MIN_DURATION = 15
SCHEDULE_CLIENT_CONTACT_CLASS = 'apps.user_func.adviser.models.Adviser'
SCHEDULE_DEFAULT_MEETING_EVENT_ID = 1
# czy tylko klienci będący przypisani do danego pracownika / doradcy
SCHEDULE_OWNED_CLIENTS_ONLY = True

NO_UPDATE_LAST_LOGIN = True
#  handler500 = 'apps.views.my_custom_error_view'
if os.name == 'nt':
    WKHTMLTOIMAGE_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
    WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    WKHTMLTOIMAGE_OPTIONS = {}
    WKHTMLTOPDF_OPTIONS = {}
else:
    WKHTMLTOIMAGE_PATH = r'/usr/bin/wkhtmltoimage'  # todo: change it to ENV variable and get from there!!!
    # WKHTMLTOPDF_PATH = r'/usr/bin/wkhtmltopdf'  # todo: change it to ENV variable and get from there!!!
    WKHTMLTOPDF_PATH = '/usr/local/bin/wkhtmltopdf'  # todo: change it to ENV variable and get from there!!!
    WKHTMLTOIMAGE_OPTIONS = {"xvfb": ""}
    WKHTMLTOPDF_OPTIONS = {}

# TESSERACT
if os.name == 'nt':
    TESSERACT_EXECUTABLE_PATH = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
else:
    TESSERACT_EXECUTABLE_PATH = r'/usr/bin/tesseract'  # todo: change it to ENV variable and get from there!!!

if DEBUG:
    import mimetypes

    mimetypes.add_type("application/javascript", ".js", True)

SMSAPI_ACCESS_TOKEN = '9xKogAHn8PKzsyqiEZVgYYLVF3rfenIySFaKu8A4'
GUSAPI_KEY = 'a36a67dd1fcb46599458'

INFINITY_DATE = datetime.datetime.strptime('99990101', '%Y%m%d').date()
MINUS_INFINITY_DATE = datetime.datetime.strptime('00010101', '%Y%m%d').date()
INITIAL_PASSWORD_LENGTH = 15

CSV_DELIMITER = ';'

BATCH_TRANSACTION_FILES_ROOT = os.path.join(BASE_DIR, '../../batch_processing')

# REST_FRAMEWORK = {
#
#     'DEFAULT_RENDERER_CLASSES': (
#         # 'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
#         # 'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
#         'rest_framework.renderers.JSONRenderer',
#         'rest_framework.renderers.BrowsableAPIRenderer',
#     ),
#
#     'DEFAULT_PARSER_CLASSES': (
#         # If you use MultiPartFormParser or FormParser, we also have a camel case version
#         # 'djangorestframework_camel_case.parser.CamelCaseFormParser',
#         # 'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
#         # 'djangorestframework_camel_case.parser.CamelCaseJSONParser',
#         'rest_framework.parsers.JSONParser',
#         # Any other parsers
#     ),
# }

ADMINS = [('3WS', 'info@3ws.pl')]

GOOGLE_MAPS_API_KEY = 'AIzaSyD2xzurQ2cqaJL83pxmG8KAMKz_4rdnHZk'

CURRENCY = 'PLN'
CURRENCY_SHORTCUT = 'zł'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        'log_to_stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        # 'file': {
        #     'level': 'DEBUG',
        #     'class': 'logging.FileHandler',
        #     'filename': '/',
        # },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
        'propagate': True,
    }
}

EMAIL_USE_TLS = True
# EMAIL_USE_SSL = True
EMAIL_HOST = 'list.home.pl'
EMAIL_HOST_USER = 'info@supercrm.com.pl'
EMAIL_HOST_PASSWORD = 'MRCrepuS11'  # os.environ.get('CRM_MAIL_PASSWORD')
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'Powiadomienia CRM <info@supercrm.com.pl>'
ADMIN_EMAIL = 'info@supercrm.com.pl'
SERVER_EMAIL = 'info@supercrm.com.pl'

CRONJOBS = []
