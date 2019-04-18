from . import qt
import sip
import asyncio

from typing import List
from .work_window import WorkWindow


class ManagerWindow(qt.QWidget):
    class WorkThread(qt.QThread):
        def __init__(self, manager: 'ManagerWindow'):
            super().__init__()
            self.manager = manager

        def run(self):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = []
            queues = dict()

            for window in self.manager.work_windows:
                try:
                    input_queue = queues[window.input_queue_name]
                except KeyError:
                    input_queue = queues.setdefault(window.input_queue_name, asyncio.Queue())

                try:
                    output_queue = queues[window.output_queue_name]
                except KeyError:
                    output_queue = queues.setdefault(window.output_queue_name, asyncio.Queue())

                window.work_process = window.process_type(
                    input_queue, output_queue, window.stdout_queue
                )

                window.work_process.loop = loop

                task = loop.create_task(
                    window.work_process.run()
                )
                window.work_process.run_task = task
                window.setWindowTitle(window.work_process.name)
                tasks.append(task)

            loop.run_until_complete(asyncio.gather(*tasks))

    def __init__(self):
        super().__init__()

        self.start_button = qt.QPushButton()
        self.start_button.setText('Start Work')
        self.start_button.clicked.connect(self.start_work)
        self.work_started = False

        def pause_all(paused):
            for window in self.work_windows:
                if not sip.isdeleted(window):
                    window.pause_button.setChecked(paused)

        self.pause_all_button = qt.QPushButton()
        self.pause_all_button.setCheckable(True)
        self.pause_all_button.setText('Pause')
        self.pause_all_button.toggled.connect(pause_all)

        self.rearrange_button = qt.QPushButton()
        self.rearrange_button.setText('Rearrange Windows')
        self.rearrange_button.clicked.connect(self.arrange_windows)

        self.mdiarea = qt.QMdiArea()
        self.mdiarea.setActivationOrder(qt.QMdiArea.CreationOrder)

        self.vboxlayout = qt.QVBoxLayout(self)
        self.vboxlayout.addWidget(self.start_button)
        self.vboxlayout.addWidget(self.pause_all_button)
        self.vboxlayout.addWidget(self.rearrange_button)
        self.vboxlayout.addWidget(self.mdiarea)

        self.input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()

        self.work_windows: List[WorkWindow] = []
        self.processes = []
        self.work_thread = ManagerWindow.WorkThread(self)

    def start_work(self):
        if not self.work_started:
            self.start_button.setEnabled(False)
            self.work_started = True
            self.work_thread.start()

            self.arrange_windows()

    def add_window(self, window: WorkWindow):
        self.work_windows.append(window)
        mdi_subwindow: qt.QMdiSubWindow = self.mdiarea.addSubWindow(window)
        mdi_subwindow.setWindowFlag(qt.constants.FramelessWindowHint)
        window.show()

    def add_process(self, process_type, input_queue_name='default', output_queue_name='default'):

        self.add_window(
            WorkWindow(input_queue_name, output_queue_name, process_type)
        )

    def arrange_windows(self):
        self.mdiarea.tileSubWindows()
        for window in self.work_windows:
            window.stdout.verticalScrollBar().setValue(
                window.stdout.verticalScrollBar().maximum()
            )

    def closeEvent(self, event: qt.QCloseEvent):

        for window in self.work_windows:
            if not sip.isdeleted(window):
                window.close()

        super().closeEvent(event)
