from . import qt

import asyncio
import threading
from queue import Queue

from .work_process import WorkProcess
from .qtextoutput import QTextOutput


class OutputThread(threading.Thread):
    class Signals(qt.QObject):
        output_received = qt.pyqtSignal(object)

    def __init__(self, output_queue: Queue):
        super().__init__()
        self.setDaemon(True)
        self.output_queue = output_queue
        self.signals = OutputThread.Signals()

    def run(self):
        while True:
            output = self.output_queue.get(block=True)
            self.signals.output_received.emit(output)


class WorkWindow(qt.QWidget):
    work_complete = qt.pyqtSignal()

    def __init__(self, input_queue_name, output_queue_name, process_type=WorkProcess):
        super().__init__()

        self.input_queue_name: asyncio.Queue = input_queue_name
        self.output_queue_name: asyncio.Queue = output_queue_name

        self.stdout = QTextOutput()
        self.stdout_queue: Queue = Queue()
        self.stdout_thread = OutputThread(self.stdout_queue)
        self.stdout_thread.signals.output_received.connect(self.stdout.write)
        self.stdout_thread.start()

        self.process_type = process_type
        self.work_process: WorkProcess = None

        self.pause_button = qt.QPushButton()
        self.pause_button.setCheckable(True)
        self.pause_button.setText('Pause')
        self.pause_button.toggled.connect(self.set_paused)

        self.vboxlayout = qt.QVBoxLayout(self)
        self.vboxlayout.addWidget(self.stdout)
        self.vboxlayout.addWidget(self.pause_button)

    def set_paused(self, paused):
        self.work_process.set_paused(paused)

    def closeEvent(self, event: qt.QCloseEvent):
        self.work_process.loop.call_soon_threadsafe(
            self.work_process.run_task.cancel
        )

        super().closeEvent(event)
