from datetime import timedelta, datetime


def time_plus(time, timedelta):
    start = datetime(
        2000, 1, 1,
        hour=time.hour, minute=time.minute, second=time.second)
    end = start + timedelta
    return end.time()

def time_minus(time, timedelta):
    start = datetime(
        2000, 1, 1,
        hour=time.hour, minute=time.minute, second=time.second)
    end = start - timedelta
    return end.time()


class Scheduler:
    def __init__(self, data_processor):
        self.data_processor = data_processor

    def full_slots_for_worker(self, time_work_start, time_work_end, tasks_start_end):
        res = {}

        current = time_work_start

        # duration = timedelta(hours=1)

        time_start = current

        count = 0

        while current != time_work_end:
            # todo: упростить (через dict)
            for task in tasks_start_end:
                if current == task['start']:
                    current = task['end']
                    time_start = current
                    count = 0
                    continue

            current = time_plus(current, timedelta(hours=1))

            # # duration_timestart-time-end
            res['{0}-{1}'.format(time_start, current)] = None

            for i in range(count):
                res['{0}-{1}'.format(time_minus(time_start, timedelta(hours=count)), current)] = None

            time_start = current
            count += 1

        # print(time_work_start, time_work_end, tasks_start_end)

        for i in res:
            print(i)

        print()
        return res

    async def get_full_free_slots(self):
        res = {}

        workers_and_tasks = await self.data_processor.get_workers_and_tasks()

        for worker_and_task in workers_and_tasks:
            values = workers_and_tasks[worker_and_task]

            time_work_start = values[0]['work_start']
            time_work_end = values[0]['work_end']

            tasks_start_end = []

            for val in values:
                time_start = val['time_start']

                # no one task on worker
                if time_start is None:
                    break

                tasks_start_end.append({
                    "start": time_start,
                    "end": val['time_end']
                })

            print(time_work_start, time_work_end, tasks_start_end)
            full_slots_for_worker = self.full_slots_for_worker(time_work_start, time_work_end, tasks_start_end)

            res.update(full_slots_for_worker)

            break

        return res

    async def find_available_slots(self):
        get_full_free_slots = await self.get_full_free_slots()
        for free_slot in get_full_free_slots:
            # print(free_slot)
            pass

        # todo: algorithm to remove not possible slots
