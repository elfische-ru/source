import sys
import os
import datetime
import json
from google.appengine.api import channel
from google.appengine.api import memcache
import django.utils.html

sys.path.append(os.path.dirname(os.getcwd()))
import model


class Chat:
    def create_user(self):
        stream_user_id = 'user_%s' % memcache.incr('user_ids_counter', initial_value = 0)
        users = memcache.get('char_user_ids')
        if not users:
            users = [stream_user_id]
        else:
            users.append(stream_user_id)
        memcache.set('char_user_ids', users)
        self.sent_to_all({'users_count': len(users)})
        return {
            'tocken': channel.create_channel(stream_user_id),
            'id': stream_user_id,
        }

    def disconnect_user(self, stream_user_id):
        users = memcache.get('char_user_ids')
        if users and stream_user_id in users:
            users.remove(stream_user_id)
            memcache.set('char_user_ids', users)
        self.sent_to_all({'users_count': len(users)})

    def to_unix_time(self, dt):
        return (dt - datetime.datetime(1970, 1, 1)).total_seconds()

    def write(self, msg):
        created = datetime.datetime.now()
        model.Chat(msg = msg, created = created).put()
        self.sent_to_all({
            'add_message': {
                'msg': django.utils.html.escape(msg),
                'created': self.to_unix_time(created)
            }
        })

    def get_users_count(self):
        users = memcache.get('char_user_ids')
        return len(users) if users else 0

    def get_last_messages(self):
        q = model.Chat.all()
        q.order('-created')
        out = []
        for i in q.run(limit=30):
            out.append({
                'msg': django.utils.html.escape(i.msg),
                'created': self.to_unix_time(i.created)
            })
        return out

    def sent_to_all(self, data):
        users = memcache.get('char_user_ids')
        if users:
            for stream_user_id in users:
                self.send_to_user(stream_user_id, data)

    def send_to_user(self, stream_user_id, data):
        channel.send_message(stream_user_id, json.dumps(data))

    def check_users(self):
        users = memcache.get('char_user_ids')
        last_check = memcache.get('last_check_users')
        if last_check:
            for stream_user_id in last_check:
                self.disconnect_user(stream_user_id)

        new_check = {}
        if users:
            for stream_user_id in users:
                self.send_to_user(stream_user_id, {'check_user': True})

        memcache.set('last_check_users', users)

    def check_user_live(self, stream_user_id):
        last_check = memcache.get('last_check_users')
        last_check.remove(stream_user_id)
        memcache.set('last_check_users', last_check)


chat               = Chat()
create_user        = chat.create_user
write              = chat.write
get_last_messages  = chat.get_last_messages
sent_to_all        = chat.sent_to_all
disconnect_user    = chat.disconnect_user
get_users_count    = chat.get_users_count
check_users        = chat.check_users
check_user_live    = chat.check_user_live
