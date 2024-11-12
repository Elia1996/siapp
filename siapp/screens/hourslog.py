from datetime import datetime
from typing import Literal
from siapp.db.database import (
    current_state,
    set_work_log,
    analyze_hours,
    get_hourslog_data_summary,
    save_exported_data,
    get_fmanager_path,
    get_worked_hours_today,
    delete_workday_entry,
)
from kivymd.uix.filemanager import (
    MDFileManager,
)  # Usa MDFileManager al posto di FileChooserIconView
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import (
    MDDatePicker,
    MDTimePicker,
)

Builder.load_file("siapp/screens/hourslog.kv")


class MyLabelBox(MDBoxLayout):
    title_text = StringProperty("")
    main_text = StringProperty("")
    main_text_opacity = StringProperty("0")
    box_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class HoursLogScreen(MDScreen):
    loggedin = (0.745, 0, 0, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=False,
        )
        self._excel_output_path = None
        self.menu = None

    def open_menu(self, root):
        menu_items = [
            {
                "text": "Edit",
                "on_release": lambda x="edit": self.menu_callback(x, root),
            },
            {
                "text": "Delete",
                "on_release": lambda x="delete": self.menu_callback(x, root),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=root.ids.option_button, items=menu_items, width_mult=3
        )
        self.menu.open()

    def menu_callback(self, text_item, root):
        if text_item == "edit":
            self.menu.dismiss()
        elif text_item == "delete":
            delete_workday_entry(root.workday_id)
            self.update_summary_list()
            self.menu.dismiss()

    def open_file_manager_exporter(self):
        # Open file manager at the default directory or a specific one
        self.file_manager.show(get_fmanager_path())

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
            self.ids.hourslog.md_bg_color = self.theme_cls.primary_color
        self.update_summary_list()
        Clock.schedule_interval(self.update_worked_hours_today, 1)

    def update_worked_hours_today(self, dt):
        worked_hours = str(get_worked_hours_today())
        self.ids.worked_hours_today.main_text = worked_hours

    def add_log(self, button):
        # Check the current state and toggle text and color
        if button.text == "You are Logged In":
            button.text = "You are Logged Out"
            button.md_bg_color = self.theme_cls.primary_color
            set_work_log(False, datetime.now())
        else:
            button.text = "You are Logged In"
            button.md_bg_color = self.loggedin
            set_work_log(True, datetime.now())
        analyze_hours()
        self.update_summary_list()

    def update_summary_list(self):
        l_data = get_hourslog_data_summary()
        l_final_data = []
        for data in l_data:
            l_final_data.append(data)
            l_final_data[-1]["hourslogscreen"] = self

        self.ids.hours_summary.data = l_final_data

    def export(self):
        """Export data from db to an excel and ask user where to save it"""
        # Ask the user with a dialog where to save the file
        self.open_file_manager_exporter()

    def export_data(self):
        # Save the data to the selected path
        save_exported_data(self._excel_output_path)

    def add_checkin(self, instance, value):
        check_out_datetime = datetime.combine(self._new_date, value)
        print(check_out_datetime)
        set_work_log(True, check_out_datetime)
        self.update_summary_list()

    def add_checkout(self, instance, value):
        # Convert the date and time to a datetime object
        check_out_datetime = datetime.combine(self._new_date, value)
        # Save the check out time
        print(check_out_datetime)
        set_work_log(False, check_out_datetime)
        self.update_summary_list()

    def add_checkin_time(self, instance, value, date_range):
        """Open a dialog to add a checkin"""
        self._new_date = value
        time_dialog = MDTimePicker(
            time=datetime.now().time(),
        )
        time_dialog.bind(on_save=self.add_checkin)
        time_dialog.open()

    def add_checkout_time(self, instance, value, date_range):
        """Open a dialog to add a checkout"""
        self._new_date = value
        time_dialog = MDTimePicker(
            time=datetime.now().time(),
        )
        time_dialog.bind(on_save=self.add_checkout)
        time_dialog.open()

    def add_check_inout(self, check_inout: Literal["checkin", "checkout"]):
        """Open a date picker dialog"""
        on_ok_callback = None
        if check_inout == "checkin":
            on_ok_callback = self.add_checkin_time
        elif check_inout == "checkout":
            on_ok_callback = self.add_checkout_time
        date_dialog = MDDatePicker(
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
        )
        date_dialog.bind(on_save=on_ok_callback)
        return date_dialog.open()
