from qt_async_work import qt

import qt_async_work
import sys
import asyncio
import random


class TestProducer(qt_async_work.ProducerProcess):
    async def items(self):
        while True:
            value = random.random()
            self.print_stdout('produced', value)
            yield self.name, value
            await asyncio.sleep(0.05*value)


class TestConsumer(qt_async_work.ConsumerProcess):
    async def consume(self, item):
        producer, item = item
        self.print_stdout('Received item', item, 'from', producer)
        await asyncio.sleep(0.01*item)


if __name__ == '__main__':
    app = qt.QApplication(sys.argv)

    manager_window = qt_async_work.ManagerWindow()
    manager_window.show()

    for i in range(2):
        manager_window.add_process(TestProducer, output_queue_name='queue')

    for i in range(18):
        manager_window.add_process(TestConsumer, input_queue_name='queue')

    manager_window.arrange_windows()
    sys.exit(app.exec())
