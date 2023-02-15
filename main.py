from qtstrap import *
from calendar_widget import CalendarWidget


def run():
    app = BaseApplication()
    window = BaseMainWindow()

    set_font_options(window, {'setPointSize': 12})
    window.setMinimumSize(400, 300)

    calendar = CalendarWidget()

    with CVBoxLayout(window) as layout:
        with layout.hbox(align='center') as layout:
            layout.add(calendar)

    window.show()
    app.exec_()

 
if __name__ == "__main__":
    run()
