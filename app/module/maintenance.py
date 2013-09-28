import sys
import os
from google.appengine.ext import db

sys.path.append(os.path.dirname(os.getcwd()))
import model


from google.appengine.ext import deferred
from google.appengine.ext import db

BATCH_SIZE = 100  # ideal batch size may vary based on entity size.

def UpdateSchema(cursor=None, num_updated=0):
    query = model.ChatProduction.all()
    if cursor:
        query.with_cursor(cursor)

    to_put = []
    for p in query.fetch(limit=BATCH_SIZE):
        p.lang = db.Category('ru')
        to_put.append(p)

    if to_put:
        db.put(to_put)
        num_updated += len(to_put)
        deferred.defer(
            UpdateSchema, cursor=query.cursor(), num_updated=num_updated)
    else:
        # complete
        pass


def start():
    UpdateSchema()
