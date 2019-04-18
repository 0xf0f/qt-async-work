from .work_process import WorkProcess


class ProducerProcess(WorkProcess):
    async def work(self):
        async for item in self.items():
            await self.pause_flag.wait()
            await self.output_queue.put(item)

    async def items(self):
        for i in ():
            yield i
