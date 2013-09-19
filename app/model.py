import datetime
from google.appengine.ext import db


class ChatProduction(db.Model):
    msg = db.StringProperty()
    created = db.DateTimeProperty()

class ChatTest01(db.Model):
    msg = db.StringProperty()
    created = db.DateTimeProperty()


Chat = ChatProduction
# Chat = ChatTest01
