import io
import asyncio
import traceback

from queue import Queue


class StopWork:
    pass


class WorkProcess:
    instances = 0

    def __init__(self, input_queue, output_queue, stdout_queue, name=None):
        super().__init__()

        if name is None:
            name = f'{self.__class__.__name__}-{self.__class__.instances}'
            self.__class__.instances += 1

        self.name = name

        self.input_queue: asyncio.Queue = input_queue
        self.output_queue: asyncio.Queue = output_queue

        self.stdout_queue: Queue = stdout_queue

        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.run_task: asyncio.Task = self.loop.create_task(self.run())

        self.pause_flag = asyncio.Event()
        self.set_paused(False)

    async def run(self) -> None:
        try:
            await self.started()
            await self.work()
            await self.finished()

        except Exception:
            self.print_stdout(traceback.format_exc())

    async def started(self):
        pass

    async def work(self):
        pass

    async def finished(self):
        pass

    def print_stdout(self, *args):
        string = io.StringIO()
        print(*args, file=string)
        self.stdout_queue.put(string.getvalue())

    def set_paused(self, paused: bool):
        if paused:
            self.loop.call_soon_threadsafe(
                self.pause_flag.clear
            )

        else:
            self.loop.call_soon_threadsafe(
                self.pause_flag.set
            )
