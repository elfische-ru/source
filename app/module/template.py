'''
Source code for http://www.elfische.ru website.
Released under the MIT license (http://opensource.org/licenses/MIT).
'''
import os
import json
import re
import jinja2
import gettext
from lib import mobilebrowser


DEBUG = 'Development' in os.environ['SERVER_SOFTWARE']
APP_VERSION = os.environ['CURRENT_VERSION_ID'].split('.')[0]


if DEBUG:
    import local_settings
    STATIC_URL = local_settings.STATIC_URL % APP_VERSION
else:
    STATIC_URL = 'http://elfische-ru.github.io/static/build/%s' % APP_VERSION


class Template:
    def __init__(self):
        self.jinja2 = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(__file__), '../templates')
            ),
            extensions=['jinja2.ext.i18n'],
        )

    def set_locale(self, lang):
        self.lang = lang
        self.jinja2.install_gettext_translations(
            gettext.translation('base', 'locale', languages=[lang])
        )
        self.js_translations = self.get_js_translations(
            gettext.translation('js', 'locale', languages=[lang])
        )

    def get_js_translations(self, translations):
        keys = translations._catalog.keys()
        keys.sort()

        ret = {'catalog': {}}
        for key in keys:
            item = translations._catalog[key]
            if type(key) is tuple:
                if key[0] not in ret['catalog']:
                    ret['catalog'][key[0]] = []
                ret['catalog'][key[0]].append(item)
            else:
                plural_forms = re.search(
                    r'Plural-Forms: nplurals=(?P<nplurals>\d+); plural=(?P<plural>.*)',
                    item
                )
                if plural_forms:
                    ret['plural'] = plural_forms.group('plural')
                    ret['nplurals'] = int(plural_forms.group('nplurals'))

        return ret

    def get_header_files(self, css=[], js=[]):
        app_verion_full = os.environ['CURRENT_VERSION_ID']
        out = []
        for i in css:
            out.append(
                '<link rel="stylesheet" type="text/css" href="%s/css/%s.css?%s" />'
                % (STATIC_URL, i, app_verion_full)
            )

        for i in js:
            out.append(
                '<script src="%s?%s"></script>' % (
                    '%s/js%s' % (STATIC_URL, i[1]) if i[0] == 'static' else i[1],
                    app_verion_full
                )
            )
        return ''.join(out)

    def render(self, name, data={}, js_data={}, css=[], js=[], request=None):
        is_mobile = (
            mobilebrowser.detect(request.headers.get('User-Agent', ''))
            if request else
            False
        )

        template_js_data = {
            'is_mobile': is_mobile,
            'debug': DEBUG,
            'js_translations': self.js_translations,
        }
        template_js_data.update(js_data)

        template_data = {
            'js_data': json.dumps(template_js_data),
            'static_url': STATIC_URL,
            'is_mobile': is_mobile,
            'app_version': APP_VERSION,
            'header_files': self.get_header_files(css, js),
            'lang': self.lang,
        }
        template_data.update(data)

        return self.jinja2.get_template('%s.jinja2' % name).render(template_data)


template = Template()
render = template.render
set_locale = template.set_locale
