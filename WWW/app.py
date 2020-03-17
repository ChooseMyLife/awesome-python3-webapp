from aiohttp import web
from datetime import datetime
import time
import json
import os
import asyncio
import logging
import orm
from models import User, Blog, Comment
logging.basicConfig(level=logging.INFO)


def index(request):
    return web.Response(body=b'<h1>Awesome</h1>', content_type='text/html')


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv

loop = asyncio.get_event_loop()


loop.run_until_complete(init(loop))
loop.run_forever()

# async def test():
#     await orm.create_pool(user='root', password='1234', db='awesome', loop=loop)
#     u = User(name='Test', email='test@qq.com', admin=False,
#              passwd='1234567890', image='about:black', created_at=time.time())
#     await u.save()
# loop.run_until_complete(test())
