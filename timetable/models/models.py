class Worker:
    def __init__(self,
                 full_name=None,
                 work_start=None,
                 work_end=None,
                 fully_loaded=None,
                 today_work=None):
        self.full_name = full_name
        self.work_start = work_start
        self.work_end = work_end
        self.fully_loaded = fully_loaded
        self.today_work = today_work


class Task:
    def __init__(self,
                 worker_id=None,
                 time_start=None,
                 time_end=None,
                 duration=None):
        self.worker_id = worker_id
        self.time_start = time_start
        self.time_end = time_end
        self.duration = duration


class Slot:
    def __init__(self, time_start, duration):
        self.time_start = time_start
        self.duration = duration
