
import os


server_software = os.environ.get('SERVER_SOFTWARE')
DEBUG = 'Development' in server_software if server_software else False

app_verion = os.environ.get('CURRENT_VERSION_ID')
APP_VERSION = app_verion.split('.')[0] if app_verion else None

if DEBUG:
    import local_settings
    STATIC_URL = local_settings.STATIC_URL % APP_VERSION
else:
    STATIC_URL = 'http://elfische-ru.github.io/static/build/%s' % APP_VERSION
