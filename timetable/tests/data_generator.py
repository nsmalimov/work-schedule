import asyncio
from datetime import timedelta, datetime

import yaml

from timetable.db_worker.psql_worker import PSQLWorker
from timetable.models.models import Worker, Task


def read_test_data_from_yaml_file():
    # 10:00:00 will be seconds from 00:00:00
    # 00:00:00 - '00:00:00' instead
    with open('test_data.yaml', 'r') as stream:
        return yaml.safe_load(stream)


def parse_timestamp(timestamp):
    if isinstance(timestamp, int):
        return datetime.strptime('00:00:00', '%H:%M:%S') + timedelta(seconds=int(timestamp))
    else:
        return datetime.strptime(timestamp, '%H:%M:%S')


def parse_duration(duration):
    duration_splitted = duration.split(' ')

    # от 30 минут до 4 часов
    # не стал делать через секунды, хотел сохранить psql-стайл интервалов
    if duration_splitted[1] == 'minutes':
        return timedelta(seconds=int(duration_splitted[0]))
    elif duration_splitted[1] == 'hours':
        return timedelta(hours=int(duration_splitted[0]))
    else:
        raise Exception('Unknown duration[yaml] data: {0}'.format(duration))


def get_test_data_workers_tasks():
    test_data_from_yaml = read_test_data_from_yaml_file()

    res = {
        'workers': [],
        'tasks': []
    }

    for i in test_data_from_yaml:
        if i['table'] == 'worker':
            d = i['fields']

            if 'work_start' in d:
                d['work_start'] = parse_timestamp(d['work_start'])

            if 'work_end' in d:
                d['work_end'] = parse_timestamp(d['work_end'])

            res['workers'].append(Worker(**d))
        else:
            d = i['fields']

            if 'time_start' in d:
                d['time_start'] = parse_timestamp(d['time_start'])

            if 'time_end' in d:
                d['time_end'] = parse_timestamp(d['time_end'])

            d['duration'] = parse_duration(d['duration'])

            res['tasks'].append(Task(**i['fields']))

    return res


async def main():
    pSQLWorker = None
    try:
        test_data = get_test_data_workers_tasks()

        pSQLWorker = PSQLWorker()
        await pSQLWorker.init_connect(
            user='postgres',
            password='123',
            database='timetable',
            host='localhost'
        )

        for worker in test_data['workers']:
            await pSQLWorker.insert_worker(worker)

        for task in test_data['tasks']:
            await pSQLWorker.insert_task(task)
    finally:
        if not (pSQLWorker is None):
            await pSQLWorker.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
