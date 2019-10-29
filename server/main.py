from aiohttp import web
import logging
from server.handlers import handlers
from timetable.db_worker.psql_worker import PSQLWorker
from timetable.scheduler.scheduler import Scheduler

IS_DEBUG = True

async def on_shutdown(app):
    await app.psql_worker.close()


async def init_app():
    app = web.Application()

    app.router.add_get('/', handlers.index)
    app.router.add_get('/workers', handlers.get_workers)
    app.router.add_get('/tasks', handlers.get_tasks)
    app.router.add_get('/free_slots', handlers.get_free_slots)

    app.router.add_static('/static', './static')

    app.on_shutdown.append(on_shutdown)

    app.psql_worker = PSQLWorker()
    await app.psql_worker.init_connect(
        user='postgres',
        password='123',
        database='timetable',
        host='localhost'
    )

    app.scheduler = Scheduler(app.psql_worker)

    # important
    app.server_url = 'http://localhost'
    # app.server_url = 'http://92.53.91.203'

    if IS_DEBUG:
        logging.basicConfig(level=logging.INFO)

    return app


if __name__ == "__main__":
    web.run_app(init_app())
