from datetime import datetime
import os
from siapp.db.database import (
    current_state,
    set_work_log,
    analyze_hours,
    get_data_summary,
    save_exported_data,
)
from kivymd.uix.filemanager import (
    MDFileManager,
)  # Usa MDFileManager al posto di FileChooserIconView
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder

Builder.load_file("screens/hourslog.kv")


class HoursLogScreen(MDScreen):
    loggedin = (1, 0, 0, 1)
    loggedout = (0, 1, 0, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=False,
        )
        self._excel_output_path = None

    def open_file_manager_exporter(self):
        # Open file manager at the default directory or a specific one
        self.file_manager.show(
            os.path.expanduser("~")
        )  # Opens at the home directory

    def select_path(self, path):
        # Here you get the selected folder path
        self.exit_manager()  # Close the file manager
        self._excel_output_path = path
        self.export_data()

    def exit_manager(self, *args):
        # Close the file manager
        self.file_manager.close()

    def on_enter(self):
        state = current_state()
        if state:
            self.ids.hourslog.text = "You are Logged In"
            self.ids.hourslog.md_bg_color = self.loggedin
        else:
            self.ids.hourslog.text = "You are Logged Out"
            self.ids.hourslog.md_bg_color = self.loggedout

    def add_log(self, button):
        # Check the current state and toggle text and color
        if button.text == "You are Logged In":
            button.text = "You are Logged Out"
            button.md_bg_color = self.loggedout
            set_work_log(False, datetime.now())
        else:
            button.text = "You are Logged In"
            button.md_bg_color = self.loggedin
            set_work_log(True, datetime.now())
        analyze_hours()
        self.update_summary_list()

    def update_summary_list(self):
        l_data = get_data_summary()
        print(l_data)
        self.ids.hours_summary.data = l_data

    def export(self):
        """Export data from db to an excel and ask user where to save it"""
        # Ask the user with a dialog where to save the file
        self.open_file_manager_exporter()

    def export_data(self):
        # Save the data to the selected path
        save_exported_data(self._excel_output_path)
