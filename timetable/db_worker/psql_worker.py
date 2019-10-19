import asyncpg


class PSQLWorker:
    def __init__(self):
        self.connection = None

    async def init_connect(self, user, password, database, host):
        conn = await asyncpg.connect(user=user, password=password,
                                     database=database, host=host)

        self.connection = conn

    async def get_available_workers_and_tasks(self):
        workers, tasks = [], []

        # Работники должны иметь доступное время для работы
        # остальных не вынимаем

        # Таски должны быть свободными

        return workers, tasks

    async def close(self):
        if self.connection is None:
            return

        await self.connection.close()

    async def insert_worker(self, worker):
        if self.connection is None:
            raise Exception('No connection to db')

        print(worker.__dict__)
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
