'''
Source code for http://www.elfische.ru website.
Released under the MIT license (http://opensource.org/licenses/MIT).
'''
import os
from jinja2 import nodes
from jinja2.ext import Extension


DEBUG = 'Development' in os.environ['SERVER_SOFTWARE']
APP_VERSION = os.environ['CURRENT_VERSION_ID'].split('.')[0]


if DEBUG:
    import local_settings
    STATIC_URL = local_settings.STATIC_URL % APP_VERSION
else:
    STATIC_URL = 'http://elfische-ru.github.io/static/build/%s' % APP_VERSION


class PageFilesExtension(Extension):
    tags = set(['pagefiles'])
    args_count = 2

    def get_args(self, parser):
        args = []
        if parser.stream.current.type != 'block_end':
            while True:
                args.append(parser.parse_expression())
                if not parser.stream.skip_if('comma'):
                    break
        return args

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        args = self.get_args(parser)
        body = parser.parse_statements(['name:endpagefiles'], drop_needle=True)

        return nodes.CallBlock(
            self.call_method('_render', args),
            [],
            [],
            body
        ).set_lineno(lineno)

    def _render(self, file_type=None, link_type=None, caller=None):
        app_verion_full = os.environ['CURRENT_VERSION_ID']

        dom_item_link = (
            '%s/css/%s?%s'
            if file_type == 'css' else
            '%s/js/%s?%s'
        )

        dom_item = (
            '<link rel="stylesheet" type="text/css" href="%s" />'
            if file_type == 'css' else
            '<script src="%s"></script>'
        )

        items = []
        for item in caller().strip().splitlines():
            item = item.strip()
            url = (
                item
                if link_type == 'extern' else
                dom_item_link % (STATIC_URL, item, app_verion_full)
            )

            items.append(dom_item % url)

        return ''.join(items)
