import sys
import os
from google.appengine.ext import db
from google.appengine.ext import deferred
import model

BATCH_SIZE = 100  # ideal batch size may vary based on entity size.


def UpdateSchema(cursor=None):
    # pass
    query = model.ChatProduction.all()
    if cursor:
        query.with_cursor(cursor)

    to_put = []
    for p in query.fetch(limit=BATCH_SIZE):
        # p.lang = db.Category('ru')
        p.hidden = False
        to_put.append(p)

    if to_put:
        # db.delete(to_put)
        # db.put(to_put)
        deferred.defer(UpdateSchema, cursor=query.cursor())
    else:
        # complete
        pass


def start():
    UpdateSchema()
