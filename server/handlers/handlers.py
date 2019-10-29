import json
import logging
import time

from aiohttp import web


def custom_json_serializer(object):
    return json.dumps(object, default=str)


# todo: render via template [urls]
async def index(request):
    return web.FileResponse('./static/index.html')


async def get_workers(request):
    response = {}
    status = 200

    try:
        workers = await request.app.psql_worker.get_workers()

        response['result'] = workers
    except Exception as e:
        status = 500
        logging.error(e)
        response['error_msg'] = str(e)

    return web.json_response(response, dumps=custom_json_serializer, status=status)


async def get_tasks(request):
    response = {}
    status = 200

    try:
        tasks = await request.app.psql_worker.get_tasks()

        response = {
            'result': tasks
        }
    except Exception as e:
        status = 500
        logging.error(e)
        response['error_msg'] = str(e)

    return web.json_response(response, dumps=custom_json_serializer, status=status)


async def get_free_slots(request):
    response = {}
    status = 200

    try:
        start = time.time()

        free_slots = await request.app.scheduler.find_available_slots()

        # в классе разделить методы? (не создавать объекты)
        for i in range(len(free_slots)):
            free_slots[i] = free_slots[i].__dict__

        end = time.time()
        logging.info('find_available_slots time: {0}'.format(end - start))

        response = {
            'result': free_slots
        }
    except Exception as e:
        status = 500
        logging.error(e)
        response['error_msg'] = str(e)

    return web.json_response(response, dumps=custom_json_serializer, status=status)
