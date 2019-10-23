import pytest
from timetable.db_worker.psql_worker import PSQLWorker
from timetable.scheduler.scheduler import Scheduler

async def get_pSQLWorker():
    pSQLWorker = PSQLWorker()

    await pSQLWorker.init_connect(
        user='postgres',
        password='123',
        database='timetable',
        host='localhost'
    )

    return pSQLWorker

@pytest.mark.asyncio
async def test_some_asyncio_code():
    pSQLWorker = await get_pSQLWorker()

    workers_with_tasks = await pSQLWorker.get_workers_with_tasks()

    for i in workers_with_tasks:
        print (i)

    assert  1 == 1