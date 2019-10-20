import asyncio

from timetable.db_worker.psql_worker import PSQLWorker
from timetable.scheduler.scheduler import Scheduler


async def main():
    pSQLWorker = None

    try:
        pSQLWorker = PSQLWorker()

        await pSQLWorker.init_connect(
            user='postgres',
            password='123',
            database='timetable',
            host='localhost'
        )

        scheduler = Scheduler(pSQLWorker)
        available_slots = await scheduler.find_available_slots()

        # scheduler.print_slots(available_slots)
    finally:
        if not (pSQLWorker is None):
            await pSQLWorker.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
