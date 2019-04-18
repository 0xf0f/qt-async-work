from . import qt


class QTextOutput(qt.QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.new_line_cursor = qt.QTextCursor(self.document())

    def write(self, data):
        scroll = False
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            scroll = True

        self.new_line_cursor.movePosition(self.new_line_cursor.End)
        self.new_line_cursor.insertText(data)

        if scroll:
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())