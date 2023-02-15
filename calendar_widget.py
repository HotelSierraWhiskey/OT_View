from datetime import datetime
from qtstrap import *
from PySide2.QtCore import *
from calendar import Calendar
from menu import MainMenuBar, LoginStatusLabel
from scraper import Scraper


SFE_URL = 'https://tdsb.eschoolsolutions.com'


class DayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.date = None
        self.jobs = []

        policy = self.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(policy)

        self.content = QTextEdit()
        self.content.setReadOnly(True)

        self.active_color = '#F5F7FA'
        self.inactive_color = '#FFFFFF'

        self.content.setStyleSheet(self.style_color(self.inactive_color))

        with CVBoxLayout(self) as layout:
            layout.setContentsMargins(0, 0, 0, 0)
            layout.add(self.content)

    def write_line(self, data):
        self.content.setText(data + '\n')

    def update(self):
        day_of_month = str(self.date[2])

        self.write_line(day_of_month + '\n')

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

    def event(self, ev):
        if ev.type() == QEvent.Type.Enter:
            self.content.setStyleSheet(self.style_color(self.active_color))

        if ev.type() == QEvent.Type.Leave:
            self.content.setStyleSheet(self.style_color(self.inactive_color))
        return True


class MonthWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.days = [[DayWidget() for _ in range(7)] for _ in range(6)]

        with CVBoxLayout(self) as layout:
            for week in self.days:
                with layout.hbox() as layout:
                    layout.add(week)


class DateLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.month = QLabel()
        self.year = QLabel()

        with CVBoxLayout(self) as layout:
            with layout.hbox(align='center') as layout:
                layout.add(self.month)
                layout.add(self.year)


class CalendarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scraper = Scraper(SFE_URL)
        self.menu = MainMenuBar(scraper=self.scraper)

        self.login_status_label = LoginStatusLabel()

        self.calendar = Calendar()

        self.month_index = None
        self.year_index = None

        self.date_label = DateLabel()

        self.dates = None

        self.current_month = MonthWidget()

        self.prev_button = QPushButton('Previous', clicked=self.previous)
        self.next_button = QPushButton('Next', clicked=self.next)

        self.weekdays = ['Monday', 'Tuesday', 'Wednesday',
                         'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.months = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']

        self.menu.file_submenu.login_popup.login_status_signal.connect(
            self.login_status_label.set_connected)

        self.menu.file_submenu.login_popup.login_status_signal.connect(
            self.update)

        self.menu.file_submenu.login_popup.login_status_signal.connect(
            self.reset)

        self.reset()

        with CVBoxLayout(self) as layout:
            with layout.hbox(align='left') as layout:
                layout.add(self.menu)
            with layout.hbox(align='left') as layout:
                layout.add(self.login_status_label)
            with layout.hbox(align='right') as layout:
                layout.add(self.prev_button)
                layout.add(self.next_button)

            with layout.hbox(align='center') as layout:
                layout.add(self.date_label)

            with layout.hbox() as layout:
                for day in self.weekdays:
                    layout.add(QLabel(day))

            with layout.hbox() as layout:
                layout.add(self.current_month)

    def reset(self):
        date = datetime.now()
        self.month_index = date.month
        self.year_index = date.year
        self.update_dates(date.year, date.month)

    def update_dates(self, year, month):
        def get_dates(): return self.calendar.itermonthdays4(year, month)
        self.dates = get_dates()

        self.date_label.month.setText(self.months[self.month_index - 1])
        self.date_label.year.setText(str(self.year_index))

        for week in self.current_month.days:
            for day in week:
                try:
                    day.show()
                    current_day = next(self.dates)
                    day.date = current_day

                    if self.scraper.schedule:
                        self.check_for_job(day)

                    day.update()

                except StopIteration:
                    pass

        if len(list(get_dates())) == 35:
            for day in self.current_month.days[-1]:
                day.hide()

    def previous(self):
        if self.month_index <= 1:
            self.month_index = 12
            self.year_index -= 1
        else:
            self.month_index -= 1

        self.update_dates(self.year_index, self.month_index)

    def next(self):
        if self.month_index >= 12:
            self.month_index = 1
            self.year_index += 1
        else:
            self.month_index += 1

        self.update_dates(self.year_index, self.month_index)

    def check_for_job(self, day):
        if day.date:
            for job in self.scraper.schedule:
                if job['job_start_date'] == day.date[:-1]:
                    day.jobs.append(job)

    def update(self):
        self.scraper.get_assignments()
