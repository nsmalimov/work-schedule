import asyncpg
from timetable.models.models import Task

# Не очень удачное название класса, скорее это DataProcessor
class PSQLWorker:
    def __init__(self):
        self.connection = None

    async def init_connect(self, user, password, database, host):
        conn = await asyncpg.connect(user=user, password=password,
                                     database=database, host=host)

        self.connection = conn

    async def get_free_tasks(self):
        res = []
        values = await self.connection.fetch('''SELECT *
                            FROM task WHERE worker_id is null''')


        for i in values:
            d = dict(i)
            del d['id']
            res.append(Task(**d))

        return res

    async def get_workers_with_tasks(self):
        # Работники должны иметь доступное время для работы и вообще сегодня работать
        # остальных не вынимаем

        res = {}
        values = await self.connection.fetch('''SELECT *
                    FROM task t
                    RIGHT JOIN worker w ON t.worker_id = w.id where
                     w.fully_loaded = false and
                     w.today_work = true''')

        # проще? через объект
        for i in values:
            d = dict(i)

            if d['id'] in res:
                res[d['id']].append(d)
            else:
                res[d['id']] = [d]

        return res

    async def close(self):
        if self.connection is None:
            return

        await self.connection.close()

    async def insert_worker(self, worker):
        if self.connection is None:
            raise Exception('No connection to db')

        await self.connection.execute('''
            INSERT INTO worker (full_name, work_start, work_end, fully_loaded, today_work) VALUES
            ($1, $2, $3, $4, $5)
        ''', worker.full_name, worker.work_start, worker.work_end,
                                      worker.fully_loaded, worker.today_work)

    async def insert_task(self, task):
        if self.connection is None:
            raise Exception('No connection to db')

        await self.connection.execute('''
            INSERT INTO task (worker_id, time_start, time_end, duration) VALUES
            ($1, $2, $3, $4)
        ''', task.worker_id, task.time_start, task.time_end, task.duration)
