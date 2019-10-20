from datetime import timedelta, datetime

from timetable.models.models import Slot


def time_add(time, timedelta, plus):
    start = datetime(
        2000, 1, 1,
        hour=time.hour, minute=time.minute, second=time.second)

    end = start
    if plus:
        end += timedelta
    else:
        end -= timedelta
    return end.time()


class Scheduler:
    def __init__(self, data_processor):
        self.data_processor = data_processor

    def full_slots_for_worker(self, time_work_start, time_work_end, tasks_start_end):
        res = {}

        current = time_work_start

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

            current = time_add(current, timedelta(hours=1), True)

            # duration_timestart-time-end
            res['{0}_{1}-{2}'.format(1, time_start, current)] = None

            for i in range(count):
                res['{0}_{1}-{2}'.format(count + 1,
                                         time_add(time_start, timedelta(hours=count), False),
                                         current)] = None

            time_start = current
            count += 1

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

            full_slots_for_worker = self.full_slots_for_worker(time_work_start, time_work_end, tasks_start_end)

            res.update(full_slots_for_worker)

        return res

    async def get_available_free_slots(self, full_free_slots):
        return full_free_slots

    async def find_available_slots(self):
        # получаем все возможные варианты слотов для существующих воркеров (с учётом работы и взятых тасков)
        full_free_slots = await self.get_full_free_slots()

        # удаляем невозможные слоты с учётом "не взятых" тасков
        available_free_slots = await self.get_available_free_slots(full_free_slots)

        slots = []
        # 00:00:00-01:00:00
        for slot_mask in available_free_slots:
            slot_mask_splited = slot_mask.split('_')
            duration = timedelta(hours=int(slot_mask_splited[0]))

            time_splitted = slot_mask_splited[1].split('-')
            time_start = datetime.strptime(time_splitted[0], '%H:%M:%S').time()
            time_end = datetime.strptime(time_splitted[1], '%H:%M:%S').time()

            slots.append(Slot(duration, time_start, time_end))

        self.print_slots(slots)

    def print_slots(self, slots):
        slots.sort(key=lambda x: x.time_start, reverse=True)

        for slot in slots:
            time_start = slot.time_start
            time_end = slot.time_end
            duration = slot.duration.seconds // 3600

            print('{0} hours, from: {1} to {2}'.format(duration, time_start, time_end))
