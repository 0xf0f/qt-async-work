from .work_process import WorkProcess
from .work_process import StopWork


class ConsumerProcess(WorkProcess):
    async def work(self):
        while True:
            await self.pause_flag.wait()
            item = await self.input_queue.get()
            await self.pause_flag.wait()
            if item == StopWork:
                return
            await self.consume(item)

    async def consume(self, item):
        pass

    async def output(self, data):
        await self.output_queue.put(data)
