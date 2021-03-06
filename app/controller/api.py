'''
Source code for http://www.elfische.ru website.
Released under the MIT license (http://opensource.org/licenses/MIT).
'''
import json
import webapp2
from module import chat, maintenance


class ApiController(webapp2.RequestHandler):
    def get(self, action):
        if action == 'check':
            users_count = chat.get_users_count()
            self.response.out.write(users_count)
        # elif action == 'mt':
        #     maintenance.start()

    def get_response_data(self):
        out = {}
        for key in self.request.arguments():
            out[key] = self.request.get(key)
        return out

    def post(self, action):
        if action == 'chat_message':
            chat.chat_message(self.get_response_data())
        elif action == 'check_user_live':
            chat.check_user_live(self.request.get('user_id'))
        elif action == 'hide_message':
            chat.message_action(
                'hide',
                self.request.get('message_id'),
                self.request.get('visitor_id'),
            )
        elif action == 'new_connection':
            user_data = chat.create_user({
                'ip':    self.request.remote_addr,
                'agent': self.request.headers.get('User-Agent'),
                'ref':   '',
            })
            out = {
                'tocken': user_data['tocken'],
                'stream_user_id': user_data['stream_user_id'],
            }
            self.response.out.write(json.dumps(out))

class ChatController(webapp2.RequestHandler):
    def post(self, action):
        if action == 'disconnected':
            chat.disconnect_user(self.request.get('from'))

class CronController(webapp2.RequestHandler):
    def get(self):
        chat.check_users()
