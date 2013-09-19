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


def get_template(template, data={}, js_data={}, request=None):
    is_mobile = (
        mobilebrowser.detect(request.headers.get('User-Agent', ''))
        if request else
        False
    )

    template_data = {
        'static_url': STATIC_URL,
        'is_mobile': is_mobile,
        'app_version': app_version,
    }
    template_js_data = {'is_mobile': is_mobile, 'debug': DEBUG}

    template_data.update(data)
    template_js_data.update(js_data)

    return jinja_environment.get_template(template).render({
        'data': template_data,
        'js_data': json.dumps(template_js_data),
    })


class MainController(webapp2.RequestHandler):
    def get(self):
        user_data = chat.create_user()
        self.response.out.write(
            get_template(
                'new.html',
                js_data = {
                    'user_tocken': user_data['tocken'],
                    'user_id': user_data['id'],
                    'last_messages': chat.get_last_messages(),
                    'users_count': chat.get_users_count(),
                },
                request = self.request
        ))

class ApiController(webapp2.RequestHandler):
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


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')))


app = webapp2.WSGIApplication([
    ('/', MainController),
    ('/api/(.*)', ApiController),
    ('/_ah/channel/(disconnected|connected)/', ChatController),
    ('/cron/check_users', CronController),
], debug=DEBUG)
