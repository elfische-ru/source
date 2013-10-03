'''
Source code for http://www.elfische.ru website.
Released under the MIT license (http://opensource.org/licenses/MIT).
'''
import datetime
from google.appengine.ext import db


class ChatProduction(db.Model):
    msg = db.StringProperty()
    created = db.DateTimeProperty()
    lang = db.CategoryProperty(default='ru')
    hidden = db.BooleanProperty(default=False)

class VisitorsProduction(db.Model):
    date           = db.DateTimeProperty(auto_now_add=True)
    stream_user_id = db.StringProperty()
    ip             = db.StringProperty()
    agent          = db.StringProperty()
    tocken         = db.StringProperty()

class MessageActionsProduction(db.Model):
    date           = db.DateTimeProperty(auto_now_add=True)
    visitor_id     = db.StringProperty()
    message_id     = db.StringProperty()
    action         = db.StringProperty()

class ChatTest01(db.Model):
    msg = db.StringProperty()
    created = db.DateTimeProperty()



Chat = ChatProduction
Visitors = VisitorsProduction
MessageActions = MessageActionsProduction

# Chat = ChatTest01
