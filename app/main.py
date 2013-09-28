'''
Source code for http://www.elfische.ru website.
Released under the MIT license (http://opensource.org/licenses/MIT).
'''
import webapp2
import jinja2
import os
import json

from module import chat
from lib import mobilebrowser


DEBUG = 'Development' in os.environ['SERVER_SOFTWARE']
app_version = os.environ['CURRENT_VERSION_ID'].split('.')[0]


if DEBUG:
    import local_settings
    STATIC_URL = local_settings.STATIC_URL % app_version
else:
    STATIC_URL = 'http://elfische-ru.github.io/static/build/%s' % app_version


def get_header_files(css={}, js={}):
    app_verion_full = os.environ['CURRENT_VERSION_ID']
    out = []
    for i in css:
        out.append(
            '<link rel="stylesheet" type="text/css" href="%s%s?%s" />'
            % (STATIC_URL, i, app_verion_full)
        )

    for i in js:
        out.append(
            '<script src="%s?%s"></script>' % (
                '%s%s' % (STATIC_URL, i[1]) if i[0] == 'static' else i[1],
                app_verion_full
            )
        )
    return ''.join(out)

def get_template(template, data={}, js_data={}, css={}, js={}, request=None):
    is_mobile = (
        mobilebrowser.detect(request.headers.get('User-Agent', ''))
        if request else
        False
    )

    template_data = {
        'static_url': STATIC_URL,
        'is_mobile': is_mobile,
        'app_version': app_version,
        'header_files': get_header_files(css, js),
    }
    template_js_data = {'is_mobile': is_mobile, 'debug': DEBUG}

    template_data.update(data)
    template_js_data.update(js_data)

    return jinja_environment.get_template(template).render({
        'data': template_data,
        'js_data': json.dumps(template_js_data),
    })

class HomeController(webapp2.RequestHandler):
    def get(self):
        user_data = chat.create_user()
        self.response.out.write(
            get_template(
                'home.html',
                data = {
                    'header_css_style': True,
                },
                js_data = {
                    'user_tocken': user_data['tocken'],
                    'user_id': user_data['id'],
                    'last_messages': chat.get_last_messages(),
                    'users_count': chat.get_users_count(),
                },
                css = [
                    '/css/home.css',
                ],
                js = [
                    ('url',    '/_ah/channel/jsapi'),
                    ('url',    ('https://ajax.googleapis.com/ajax/libs/jquery'
                                '/2.0.3/jquery.min.js')),
                    ('static', '/js/lib/jquery.injectCSS.js'),
                    ('static', '/js/lib/cssanimation.min.js'),
                    ('static', '/js/lib/cssanimation.jquery.min.js'),
                    ('static', '/js/generated/home.js'),
                ],
                request = self.request
            )
        )

class ApiController(webapp2.RequestHandler):
    def get(self, action):
        if action == 'check':
            users_count = chat.get_users_count()
            self.response.out.write(users_count)
        elif action == 'mt':
            chat.maintenance()

    def post(self, action):
        if action == 'chat_message':
            chat.write(self.request.get('msg'))
        elif action == 'check_user_live':
            chat.check_user_live(self.request.get('user_id'))

class ChatController(webapp2.RequestHandler):
    def post(self, action):
        if action == 'disconnected':
            chat.disconnect_user(self.request.get('from'))

class CronController(webapp2.RequestHandler):
    def get(self):
        chat.check_users()

class PagesController(webapp2.RequestHandler):
    def get(self, page_code):
        if page_code == 'about':
            self.response.out.write(
                get_template(
                    'about.html',
                    css = [
                        '/css/about.css',
                    ],
                    request = self.request
                )
            )


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')
    )
)


app = webapp2.WSGIApplication([
    ('/', HomeController),
    ('/(about)', PagesController),
    ('/api/(.*)', ApiController),
    ('/_ah/channel/(disconnected|connected)/', ChatController),
    ('/cron/check_users', CronController),
], debug=DEBUG)
