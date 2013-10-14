'''
Source code for http://www.elfische.ru website.
Released under the MIT license (http://opensource.org/licenses/MIT).
'''
import os
import json
import re
import jinja2
from jinja2 import nodes
import gettext
from jinja2.ext import Extension
from lib import mobilebrowser
import markdown2
import md2html


DEBUG = 'Development' in os.environ['SERVER_SOFTWARE']
APP_VERSION = os.environ['CURRENT_VERSION_ID'].split('.')[0]


if DEBUG:
    import local_settings
    STATIC_URL = local_settings.STATIC_URL % APP_VERSION
else:
    STATIC_URL = 'http://elfische-ru.github.io/static/build/%s' % APP_VERSION



class JsFilesExtension(Extension):
    tags = set(['jsfiles'])

    def __init__(self, environment):
        super(JsFilesExtension, self).__init__(environment)
        environment.extend(jsfiles_template_path = '')

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endjsfiles'], drop_needle=True)
        compressed_js = '%s.js' % (
            parser
                .filename[len(self.environment.jsfiles_template_path) + 1:-7]
                .replace('/', '_')
        )
        return nodes.CallBlock(
            self.call_method('_render', [nodes.Const(compressed_js)]),
            [],
            [],
            body
        ).set_lineno(lineno)

    def _render(self, compressed_js=None, caller=None):
        app_verion_full = os.environ['CURRENT_VERSION_ID']

        body = caller()

        if not DEBUG or True:
            body = '/compressed/%s' % compressed_js

        html_scripts = []
        for js_file_name in body.splitlines():
            js_file_name = js_file_name.strip()
            add_link = '<script src="%s/js%s?%s"></script>' % (
                STATIC_URL,
                js_file_name,
                app_verion_full,
            )
            html_scripts.append(add_link)
        body = ''.join(html_scripts)

        return body


class Template:
    def __init__(self, request):
        self.request = request
        template_path = os.path.join(os.path.dirname(__file__), '../templates')
        self.jinja2 = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path),
            extensions=['jinja2.ext.i18n', JsFilesExtension],
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

    def render(self, name, data={}, js_data={}, css=[], js=[]):
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
            'header_files': self.get_header_files(css, js),
            'lang': self.lang,
        }
        template_data.update(data)

        return self.jinja2.get_template('%s.jinja2' % name).render(template_data)
