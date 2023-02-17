from qtstrap import *


class Content(QTextEdit):

    mouse_press_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def mousePressEvent(self, event: PySide2.QtGui.QMouseEvent) -> None:
        self.mouse_press_signal.emit()
        return super().mousePressEvent(event)


class DayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.date = None
        self.jobs = []

        policy = self.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(policy)

        self.content = Content()
        self.content.mouse_press_signal.connect(self.toggle_highlight)
        self.content.setReadOnly(True)
        self.content.viewport().setCursor(Qt.ArrowCursor)

        self.padding = False
        self.highlighted = False

        self.active_hover_color = '#F5F7FA'
        self.inactive_hover_color = '#FFFFFF'
        self.padding_day_color = '#D3D3D3'
        self.highlighted_color = '#FFFFBF'

        self.content.setStyleSheet(self.style_color(self.inactive_hover_color))

        with CVBoxLayout(self) as layout:
            layout.setContentsMargins(0, 0, 0, 0)
            layout.add(self.content)

    def reset(self):
        self.padding = False
        self.highlighted = False
        self.set_color()

    def update(self):
        day_of_month = f"<html><b>{str(self.date[2])}</b></html>"

        self.content.setText(day_of_month)
        self.content.append('\n')

        if not self.jobs:
            return

        for job in self.jobs:
            if job['job_start_date'] == self.date[:-1]:
                self.content.append(job['Job #'])
                self.content.append(job['Start Date/Time'])
                self.content.append(job['End Date/Time'])
                self.content.append(job['Location'])
                self.content.append(job['Classification'])
                self.content.append(job['Employee in for'])
                self.content.append(job['Work Days'])

        self.content.ensureCursorVisible()

    def style_color(self, c):
        return f'QTextEdit {{ background-color: {c} }}'

    def set_color(self):
        if self.padding:
            self.content.setStyleSheet(
                self.style_color(self.padding_day_color))
        else:
            self.content.setStyleSheet(
                self.style_color(self.inactive_hover_color))

    def toggle_highlight(self):
        if self.highlighted:
            self.set_color()
            self.highlighted = False
        else:
            self.content.setStyleSheet(
                self.style_color(self.highlighted_color))
            self.highlighted = True

    def event(self, e):
        if self.highlighted:
            return True

        if e.type() == QEvent.Type.Enter:
            self.content.setStyleSheet(
                self.style_color(self.active_hover_color))

        if e.type() == QEvent.Type.Leave:
            self.set_color()

        return True
