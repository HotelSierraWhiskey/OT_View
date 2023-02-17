from qtstrap import *
from scraper import *
from calendar_widget import CalendarWidget


class MainWindow(BaseMainWindow):

    close_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def closeEvent(self, event):
        self.close_signal.emit()
        return super().closeEvent(event)


def run():
    app = BaseApplication()

    scraper = Scraper(SFE_URL)

    calendar = CalendarWidget(scraper)

    window = MainWindow()
    window.close_signal.connect(scraper.close)

    set_font_options(window, {'setPointSize': 12})
    window.setMinimumSize(400, 300)

    with CVBoxLayout(window) as layout:
        with layout.hbox(align='center') as layout:
            layout.add(calendar)

    window.show()
    app.exec_()


if __name__ == "__main__":
    run()
