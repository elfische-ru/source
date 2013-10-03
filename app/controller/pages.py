'''
Source code for http://www.elfische.ru website.
Released under the MIT license (http://opensource.org/licenses/MIT).
'''
import webapp2
from module import chat, template


class PagesController(webapp2.RequestHandler):
    def get(self, lang=None, page=None):
        if not lang:
            accept_language = self.request.headers.get('Accept-Language')
            self.redirect('/%s' % (
                'de'
                if 'de' in accept_language and 'ru' not in accept_language else
                'ru'
            ))
        else:
            self.lang = lang
            template.set_locale(self.lang)
            out = self.get_page(page) if page else self.get_home()
            self.response.out.write(out)

    def get_home(self):
        user_data = chat.create_user({
            'ip':    self.request.remote_addr,
            'agent': self.request.headers.get('User-Agent'),
            'ref':   '',
        })
        return template.render(
            'home',
            js_data = {
                'user_tocken':    user_data['tocken'],
                'stream_user_id': user_data['stream_user_id'],
                'visitor_id':     user_data['visitor_id'],
                'last_messages':  chat.get_last_messages(),
                'users_count':    chat.get_users_count(),
            },
            css = ['home'],
            js = [
                ('url',    '/_ah/channel/jsapi'),
                ('url',    ('https://ajax.googleapis.com/ajax/libs/jquery'
                            '/2.0.3/jquery.min.js')),
                ('static', '/lib/jquery.injectCSS.js'),
                ('static', '/lib/cssanimation.min.js'),
                ('static', '/lib/cssanimation.jquery.min.js'),
                ('static', '/generated/i18n.js'),
                ('static', '/generated/home.js'),
            ],
            request = self.request
        )

    def get_page(self, page_code):
        out = ''
        if page_code == 'about':
            out = template.render(
                'locale/%s/about' % self.lang,
                css = ['about'],
                request = self.request
            )
        return out
