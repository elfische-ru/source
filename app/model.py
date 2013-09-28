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

class ChatTest01(db.Model):
    msg = db.StringProperty()
    created = db.DateTimeProperty()


Chat = ChatProduction
# Chat = ChatTest01
