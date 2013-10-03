'''
Source code for http://www.elfische.ru website.
Released under the MIT license (http://opensource.org/licenses/MIT).
'''
import webapp2
from module import chat


class ApiController(webapp2.RequestHandler):
    def get(self, action):
        if action == 'check':
            users_count = chat.get_users_count()
            self.response.out.write(users_count)
        elif action == 'mt':
            # pass
            chat.maintenance()

    def post(self, action):
        if action == 'chat_message':
            chat.write(self.request.get('msg'))
        elif action == 'check_user_live':
            chat.check_user_live(self.request.get('user_id'))
        elif action == 'hide_message':
            chat.message_action(
                'hide',
                self.request.get('message_id'),
                self.request.get('visitor_id'),
            )

class ChatController(webapp2.RequestHandler):
    def post(self, action):
        if action == 'disconnected':
            chat.disconnect_user(self.request.get('from'))

class CronController(webapp2.RequestHandler):
    def get(self):
        chat.check_users()
