from datetime import datetime
from qtstrap import *
from calendar import Calendar
from day_widget import DayWidget
from menu import MainMenuBar, LoginStatusLabel


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
    def __init__(self, scraper, parent=None):
        super().__init__(parent=parent)
        self.scraper = scraper
        self.menu_bar = MainMenuBar(scraper=self.scraper)

        self.login_status_label = LoginStatusLabel()

        self.calendar = Calendar(firstweekday=6)

        self.month_index = None
        self.year_index = None

        self.date_label = DateLabel()

        self.dates = None

        self.current_month = MonthWidget()

        self.prev_button = QPushButton('Previous', clicked=self.previous)
        self.next_button = QPushButton('Next', clicked=self.next)

        self.weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday',
                         'Thursday', 'Friday', 'Saturday']
        self.months = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']

        self.menu_bar.file_submenu.login_popup.login_status_signal.connect(
            self.login_status_label.set_connected)

        self.menu_bar.file_submenu.login_popup.login_status_signal.connect(
            self.update)

        self.menu_bar.file_submenu.login_popup.login_status_signal.connect(
            self.reset)

        self.reset()

        with CVBoxLayout(self) as layout:
            with layout.hbox(align='left') as layout:
                layout.add(self.menu_bar)
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
                    day.reset()
                    day.show()
                    current_day = next(self.dates)
                    day.date = current_day

                    if day.date[1] != month:
                        day.padding = True
                        day.set_color()

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
                if job['job_start_date'] == day.date[:-1] and job not in day.jobs:
                    day.jobs.append(job)

    def update(self):
        self.scraper.get_assignments()
