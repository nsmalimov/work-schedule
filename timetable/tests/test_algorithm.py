import pytest

from timetable.db_worker.psql_worker import PSQLWorker
from timetable.scheduler.scheduler import Scheduler

# todo: через фикстуры и моки
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
async def test_get_workers_with_tasks():
    pSQLWorker = await get_pSQLWorker()
    workers_with_tasks = await pSQLWorker.get_workers_with_tasks()

    # todo: more check
    assert len(workers_with_tasks) == 7

# todo: разделить на 2 теста
@pytest.mark.asyncio
async def test_get_full_free_slots_and_get_available_free_slots():
    pSQLWorker = await get_pSQLWorker()
    workers_with_tasks = await pSQLWorker.get_workers_with_tasks()

    scheduler = Scheduler(pSQLWorker)

    # test_cases_get_full_free_slots
    full_free_slots_by_workers = scheduler.get_full_free_slots(workers_with_tasks)

    test_cases_get_full_free_slots = {
        # work: 18:00:00 - 02:00:00
        # tasks: 20:00:00 - 00:00:00
        1: [
            "2000-01-01 18:00:00-2000-01-01 19:00:00",
            "2000-01-01 18:00:00-2000-01-01 20:00:00",
            "2000-01-01 19:00:00-2000-01-01 20:00:00",
            "2000-01-02 00:00:00-2000-01-02 01:00:00",
            "2000-01-02 00:00:00-2000-01-02 02:00:00",
            "2000-01-02 01:00:00-2000-01-02 02:00:00",
        ],
        # 10:00:00 - 22:00:00
        # tasks: 12:00:00 - 16:00:00, 16:00:00 - 18:00:00
        3: [
            '2000-01-01 10:00:00-2000-01-01 11:00:00',
            '2000-01-01 10:00:00-2000-01-01 12:00:00',
            '2000-01-01 11:00:00-2000-01-01 12:00:00',
            '2000-01-01 18:00:00-2000-01-01 19:00:00',
            '2000-01-01 18:00:00-2000-01-01 20:00:00',
            '2000-01-01 18:00:00-2000-01-01 21:00:00',
            '2000-01-01 18:00:00-2000-01-01 22:00:00',
            '2000-01-01 19:00:00-2000-01-01 20:00:00',
            '2000-01-01 19:00:00-2000-01-01 21:00:00',
            '2000-01-01 19:00:00-2000-01-01 22:00:00',
            '2000-01-01 20:00:00-2000-01-01 21:00:00',
            '2000-01-01 20:00:00-2000-01-01 22:00:00',
            '2000-01-01 21:00:00-2000-01-01 22:00:00',
        ],
        # 19:00:00 - 02:00:00
        # tasks: no
        4: ['2000-01-01 19:00:00-2000-01-01 20:00:00',
            '2000-01-01 19:00:00-2000-01-01 21:00:00',
            '2000-01-01 19:00:00-2000-01-01 22:00:00',
            '2000-01-01 19:00:00-2000-01-01 23:00:00',
            '2000-01-01 20:00:00-2000-01-01 21:00:00',
            '2000-01-01 20:00:00-2000-01-01 22:00:00',
            '2000-01-01 20:00:00-2000-01-01 23:00:00',
            '2000-01-01 20:00:00-2000-01-02 00:00:00',
            '2000-01-01 21:00:00-2000-01-01 22:00:00',
            '2000-01-01 21:00:00-2000-01-01 23:00:00',
            '2000-01-01 21:00:00-2000-01-02 00:00:00',
            '2000-01-01 21:00:00-2000-01-02 01:00:00',
            '2000-01-01 22:00:00-2000-01-01 23:00:00',
            '2000-01-01 22:00:00-2000-01-02 00:00:00',
            '2000-01-01 22:00:00-2000-01-02 01:00:00',
            '2000-01-01 22:00:00-2000-01-02 02:00:00',
            '2000-01-01 23:00:00-2000-01-02 00:00:00',
            '2000-01-01 23:00:00-2000-01-02 01:00:00',
            '2000-01-01 23:00:00-2000-01-02 02:00:00',
            '2000-01-02 00:00:00-2000-01-02 01:00:00',
            '2000-01-02 00:00:00-2000-01-02 02:00:00',
            '2000-01-02 01:00:00-2000-01-02 02:00:00']
    }

    assert list(full_free_slots_by_workers.keys()) == [1, 3, 6, 12, 10, 13, 4]

    for worker_id in full_free_slots_by_workers:
        current_case = []
        for free_slot in full_free_slots_by_workers[worker_id]:
            current_case.append(free_slot)

        if worker_id in test_cases_get_full_free_slots:
            assert current_case == test_cases_get_full_free_slots[worker_id]

    # test_get_available_free_slots
    available_free_slots = await scheduler.get_available_free_slots(full_free_slots_by_workers)

    # for ..

# todo: test create_objects_from_time_mask and print_slots