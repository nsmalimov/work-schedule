import datetime
from datetime import datetime
from datetime import timedelta

from timetable.models.models import Slot


class Scheduler:
    def __init__(self, data_processor):
        self.data_processor = data_processor

    def full_slots_for_worker(self, time_work_start, time_work_end, worker_tasks_times):
        res = {}

        current_t_start = time_work_start

        while True:
            inner_t_start = current_t_start

            for j in [1, 2, 3, 4]:
                if inner_t_start >= time_work_end:
                    break

                inner_t_start = current_t_start + timedelta(hours=j)

                can_be_added = True

                # todo: упростить (через dict) или убирать таски "до" начала текущего времени
                for task in worker_tasks_times:
                    # проверка, что слот времени лежит во временном отрезке взятого таска
                    if current_t_start >= task['start'] and current_t_start < task['end']:
                       can_be_added = False
                       break

                    if inner_t_start > task['start'] and inner_t_start < task['end']:
                        can_be_added = False
                        break

                if can_be_added:
                    time_mask = self.create_time_mask(current_t_start, inner_t_start)
                    res[time_mask] = None

            current_t_start = current_t_start + timedelta(hours=1)

            if current_t_start >= time_work_end:
                break

        return res

    def create_time_mask(self, t_start, t_end):
        return '{0}-{1}'.format(t_start, t_end)

    def create_time_masks_from_task_objects(self, tasks):
        res = {}

        for task in tasks:
            key = self.create_time_mask(task.duration.seconds // 3600, task.time_start, task.time_end)

            if key in res:
                res[key] += 1
            else:
                res[key] = 1

        return res

    def get_full_free_slots(self, workers_and_tasks):
        res = {}

        for worker_id in workers_and_tasks:
            values = workers_and_tasks[worker_id]

            time_work_start = values[0]['work_start']
            time_work_end = values[0]['work_end']

            worker_tasks_times = []

            for val in values:
                time_start = val['time_start']

                # no one task on worker
                if time_start is None:
                    break

                worker_tasks_times.append({
                    "start": time_start,
                    "end": val['time_end']
                })

            full_slots_for_worker = self.full_slots_for_worker(time_work_start, time_work_end, worker_tasks_times)

            res[worker_id] = full_slots_for_worker
        return res

    async def get_available_free_slots(self, full_free_slots_max4_by_workers):
        slots = {}

        free_tasks_object = await self.data_processor.get_free_tasks()
        free_tasks_time_mask = self.create_time_masks_from_task_objects(free_tasks_object)

        slot_by_count = {}

        for worker_id in full_free_slots_max4_by_workers:
            for slot in full_free_slots_max4_by_workers[worker_id]:
                if slot in slot_by_count:
                    slot_by_count[slot] += 1
                else:
                    slot_by_count[slot] = 1

        for slot in slot_by_count:
            print(slot)

        print()

        for task in free_tasks_time_mask:
            print(task, free_tasks_time_mask[task])

        for task_time_mask in free_tasks_time_mask:
            if task_time_mask in slot_by_count:
                slot_by_count[task_time_mask] -= 1
            else:
                # в базе оказались не валидные данные (ранее была ошибка алгоритма и был создан таск, ломающий логику)
                # по хорошему надо в тестах проверить
                duration, time_start, time_end = self.parse_data_by_slot_mask(task_time_mask)
                raise Exception('Not valid task was created early: duration: {0}, time_task_start: {1},'
                                'time_task_end: {2}'
                                .format(duration, time_start, time_end))

        return slots

    def parse_data_by_slot_mask(self, slot_mask):
        slot_mask_splited = slot_mask.split('_')
        duration = timedelta(hours=int(slot_mask_splited[0]))

        time_splitted = slot_mask_splited[1].split('-')
        time_start = datetime.strptime(time_splitted[0], '%H:%M:%S').time()
        time_end = datetime.strptime(time_splitted[1], '%H:%M:%S').time()

        return duration, time_start, time_end

    def create_objects_from_time_mask(self, available_free_slots):
        slots = []
        for slot_mask in available_free_slots:
            duration, time_start, time_end = self.parse_data_by_slot_mask(slot_mask)
            slots.append(Slot(duration, time_start, time_end))

        return slots

    def create_time_mask_from_task_object(self, available_free_slots):
        slots = []
        for slot_mask in available_free_slots:
            duration, time_start, time_end = self.parse_data_by_slot_mask(slot_mask)
            slots.append(Slot(duration, time_start, time_end))

        return slots

    # основная функция
    async def find_available_slots(self):
        # проход в базу за джоином между тасками и воркерами (фильтр по работает сегодня или нет и загружен ли на полную)
        workers_with_tasks = await self.data_processor.get_workers_with_tasks()

        # считаем все возможные варианты слотов (общее время) от 1 до 4 часов,
        # для существующих воркеров (с учётом взятых тасков)
        full_free_slots_by_workers = self.get_full_free_slots(workers_with_tasks)

        # удаляем не доступные слоты с учётом "не взятых" тасков
        available_free_slots = await self.get_available_free_slots(full_free_slots_by_workers)

        # объекты из маски времени (help - операция)
        # slots = self.create_objects_from_time_mask(available_free_slots)

        return []

    def print_slots(self, slots):
        slots.sort(key=lambda x: x.time_start, reverse=True)

        for slot in slots:
            time_start = slot.time_start
            time_end = slot.time_end
            duration = slot.duration.seconds // 3600

            print('{0} hours, from: {1} to {2}'.format(duration, time_start, time_end))
