from qtstrap import *


class LoginStatusLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_connected(False)

    def set_connected(self, status):
        if status:
            self.setStyleSheet('QLabel {color:"green"}')
            self.setText('Connected')
        else:
            self.setStyleSheet('QLabel {color:"red"}')
            self.setText('Not Connected')


class LoginPopup(QDialog):

    login_status_signal = Signal(bool)

    def __init__(self, scraper=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(350, 100)
        self.setWindowTitle("Connect")

        self.scraper = scraper

        self.username_field = QLineEdit()
        self.password_field = QLineEdit()
        self.username_field.setFixedWidth(175)
        self.password_field.setFixedWidth(175)
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.status_label = QLabel()
        self.login_button = QPushButton('Connect', clicked=self.log_in)

        with CVBoxLayout(self) as layout:
            with layout.hbox(align='left') as layout:
                layout.add(QLabel('Username:\t'))
                layout.add(self.username_field)
            with layout.hbox(align='left') as layout:
                layout.add(QLabel('Password:\t'))
                layout.add(self.password_field)
            with layout.hbox(align='right') as layout:
                layout.add(self.status_label)
                layout.add(self.login_button)

    def reset(self):
        self.login_button.setDisabled(False)
        self.password_field.clear()
        self.username_field.clear()

    def log_in(self):
        self.login_button.setDisabled(True)
        username = self.username_field.text()
        password = self.password_field.text()
        try:
            self.scraper.log_in(username, password)
            self.login_status_signal.emit(True)
            self.hide()
        except Exception as exc:
            print(exc)
            self.status_label.setText('Login attemped failed')
        finally:
            self.reset()


class FileMenu(QMenu):
    def __init__(self, scraper=None, *args, **kwargs):
        super().__init__(title='File', *args, **kwargs)

        self.login_popup = LoginPopup(scraper=scraper)

        self.addAction('Connect', self.launch_login_popup)
        self.addAction('Disconnect', lambda: print('disconnect'))
        self.addAction('Restore All', lambda: print('restore all'))
        self.addSeparator()
        self.addAction('Quit', lambda: print('quit'))

    def launch_login_popup(self):
        self.login_popup.show()


class PreferencesMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(title='Preferences', *args, **kwargs)
        self.addAction('Toggle', lambda: print('penis'))


class MainMenuBar(QMenuBar):
    def __init__(self, scraper=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        scraper.launch()

        self.file_submenu = FileMenu(scraper=scraper)
        self.preferences_submenu = PreferencesMenu()

        self.addMenu(self.file_submenu)
        self.addMenu(self.preferences_submenu)


class RightClickDayMenu(QMenu):

    edit_signal = Signal()
    restore_signal = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(title='Preferences', *args, **kwargs)
        self.current_day = None
        self.hide()
        self.addAction('Edit', self.on_edit)
        self.addAction('Restore', self.on_restore)

    def launch(self, day):
        self.current_day = day
        self.popup(QCursor.pos())

    def on_edit(self):
        self.edit_signal.emit()

    def on_restore(self):
        self.restore_signal.emit()
