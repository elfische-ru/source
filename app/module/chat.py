import sys
import os
import datetime
import json
from google.appengine.api import channel
from google.appengine.api import memcache
from google.appengine.ext import db
import django.utils.html

sys.path.append(os.path.dirname(os.getcwd()))
import model
import module.maintenance


def write(msg):
    created = datetime.datetime.now()
    model.Chat(
        msg = msg,
        created = created,
        lang=db.Category('ru')
    ).put()
    sent_to_all({
        'add_message': {
            'msg': django.utils.html.escape(msg),
            'created': to_unix_time(created)
        }
    })

def check_users():
    users = memcache.get('char_user_ids')
    print users
    last_check = memcache.get('last_check_users')
    if last_check:
        for stream_user_id in last_check:
            disconnect_user(stream_user_id)

    new_check = {}
    if users:
        for stream_user_id in users:
            send_to_user(stream_user_id, {'check_user': True})

    memcache.set('last_check_users', users)

def disconnect_user(stream_user_id):
    users = memcache.get('char_user_ids')
    if users:
        if stream_user_id in users:
            users.remove(stream_user_id)
            memcache.set('char_user_ids', users)
        sent_to_all({'users_count': len(users)})

def get_last_messages():
    # get visible
    query = model.Chat.all()
    query.order('-created')
    query.filter('lang IN', ['ru', None])
    query.filter('hidden =', False)
    visible = []
    for i in query.run(limit=30):
        visible.append({
            'id': i.key().id(),
            'msg': django.utils.html.escape(i.msg),
            'created': to_unix_time(i.created),
            'hidden': i.hidden,
        })

    # get hidden
    query = model.Chat.all()
    query.order('-created')
    query.filter('lang IN', ['ru', None])
    query.filter('hidden =', True)
    hidden = []
    for i in query.run(limit=30):
        hidden.append({
            'id': i.key().id(),
            'msg': django.utils.html.escape(i.msg),
            'created': to_unix_time(i.created),
            'hidden': i.hidden,
        })

    # merge visible and hidden
    out = []
    hidden_id = 0
    visible_id = 0
    while hidden_id < len(hidden) and visible_id < len(visible):
        if visible[visible_id]['created'] > hidden[hidden_id]['created']:
            out.append(visible[visible_id])
            visible_id += 1
        else:
            out.append(hidden[hidden_id])
            hidden_id += 1

    if hidden_id < len(hidden):
        out += hidden[hidden_id:]
    elif visible_id < len(visible):
        out += visible[visible_id:]

    return out



def create_user(user_data={}):
    stream_user_id = 'user_%s' % memcache.incr(
        'user_ids_counter',
        initial_value = 0
    )

    users = memcache.get('char_user_ids')
    if not users:
        users = [stream_user_id]
    else:
        users.append(stream_user_id)

    memcache.set('char_user_ids', users)
    sent_to_all({'users_count': len(users)})

    tocken = channel.create_channel(stream_user_id)

    visitor_id = model.Visitors(
        stream_user_id = stream_user_id,
        ip             = user_data.get('ip'),
        agent          = user_data.get('agent'),
        tocken         = tocken,
    ).put()

    return {
        'tocken': tocken,
        'stream_user_id': stream_user_id,
        'visitor_id': visitor_id.id(),
    }

def sent_to_all(data):
    users = memcache.get('char_user_ids')
    if users:
        for stream_user_id in users:
            send_to_user(stream_user_id, data)

def to_unix_time(dt):
    return (dt - datetime.datetime(1970, 1, 1)).total_seconds()

def get_users_count():
    users = memcache.get('char_user_ids')
    return len(users) if users else 0

def send_to_user(stream_user_id, data):
    channel.send_message(stream_user_id, json.dumps(data))

def maintenance():
    # module.maintenance.start()
    pass

def message_action(action, message_id, visitor_id):
    model.MessageActions(
        visitor_id     = visitor_id,
        message_id     = message_id,
        action         = action,
    ).put()

def check_user_live(stream_user_id):
    last_check = memcache.get('last_check_users')
    # leak
    if stream_user_id in last_check:
        last_check.remove(stream_user_id)
        memcache.set('last_check_users', last_check)
