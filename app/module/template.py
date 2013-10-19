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
import markdown2
import md2html
from jinja2_pagefiles import PageFilesExtension


DEBUG = 'Development' in os.environ['SERVER_SOFTWARE']
APP_VERSION = os.environ['CURRENT_VERSION_ID'].split('.')[0]


if DEBUG:
    import local_settings
    STATIC_URL = local_settings.STATIC_URL % APP_VERSION
else:
    STATIC_URL = 'http://elfische-ru.github.io/static/build/%s' % APP_VERSION


class Template:
    def __init__(self, request):
        self.request = request
        template_path = os.path.join(os.path.dirname(__file__), '../templates')
        self.jinja2 = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path),
            extensions=['jinja2.ext.i18n', PageFilesExtension],
        )
        self.jinja2.jsfiles_template_path = template_path
        self.jinja2.filters['markdown'] = self.safe_markdown

    def safe_markdown(self, text):
        md = md2html.MD2Html()
        out = md.markdown_convert(text)
        return jinja2.Markup(out)

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

    def render(self, name, data={}, js_data={}):
        is_mobile = (
            mobilebrowser.detect(self.request.headers.get('User-Agent', ''))
            if self.request and 'User-Agent' in self.request.headers else
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
            'lang': self.lang,
        }
        template_data.update(data)

        return self.jinja2.get_template('%s.jinja2' % name).render(template_data)
