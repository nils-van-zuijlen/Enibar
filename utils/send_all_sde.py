import sys
sys.path.append("../application")

import api.notes
import api.sde
import api.redis
import asyncio


loop = asyncio.get_event_loop()
loop.run_until_complete(api.redis.connect())
api.notes.rebuild_cache()

nicks = [note['nickname'] for note in api.notes.get()]
task = asyncio.ensure_future(api.sde.send_notes(nicks))
loop.run_until_complete(task)

transactions = [{'id': trans['id'],
                'note': api.notes.get(lambda x: x['firstname'] == trans['firstname'] and x['lastname'] == trans['lastname'])[0]['nickname'],
                'category': trans['category'],
                'product': trans['product'],
                'price_name': trans['price_name'],
                'quantity': trans['quantity'],
                'price': trans['price'],
               } for trans in api.transactions.get()]
task2 = asyncio.ensure_future(api.sde.send_history_lines(transactions))
loop.run_until_complete(task2)

