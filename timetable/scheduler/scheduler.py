class Scheduler:
    def __init__(self, data_processor):
        self.data_processor = data_processor

    async def find_available_slots(self):
        workers, tasks = await self.data_processor.get_available_workers_and_tasks()
        print(workers, tasks)

        # todo: algorithm to find available time slots
