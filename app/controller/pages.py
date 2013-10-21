'''
Source code for http://www.elfische.ru website.
Released under the MIT license (http://opensource.org/licenses/MIT).
'''
import webapp2
from module import chat, Template


class PagesController(webapp2.RequestHandler):
    def get(self, lang=None, page=None):
        self.template = Template(request = self.request)

        if not lang:
            accept_language = self.request.headers.get('Accept-Language')
            self.redirect('/%s' % (
                'de'
                if (
                    accept_language
                    and 'de' in accept_language
                    and 'ru' not in accept_language
                ) else
                'ru'
            ))
        else:
            self.lang = lang
            self.template.set_locale(self.lang)
            out = self.get_page(page) if page else self.get_home()
            self.response.out.write(out)

    def get_home(self):
        user_data = chat.create_user({
            'ip':    self.request.remote_addr,
            'agent': self.request.headers.get('User-Agent'),
            'ref':   '',
        })
        return self.template.render(
            'home',
            js_data = {
                'user_tocken':    user_data['tocken'],
                'stream_user_id': user_data['stream_user_id'],
                'visitor_id':     user_data['visitor_id'],
                'last_messages':  chat.get_last_messages(),
                'users_count':    chat.get_users_count(),
            },
        )

    def get_page(self, page_code):
        out = ''
        if page_code == 'about':
            out = self.template.render('about')
        if page_code == 'test':
            import test
            out = test.text()
        else:
            self.error(404)
        return out
