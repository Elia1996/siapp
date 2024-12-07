#
# Copyright (c) 2024 Elia Ribaldone.
#
# This file is part of SiApp
# (see https://github.com/Elia1996/siapp).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.#
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
    delete_worlkog_entry,
    get_worklog_data_summary,
    get_last_workday_id,
)
from siapp.db.models import create_database
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
from kivymd.uix.chip import MDChip, MDChipText

Builder.load_file("siapp/screens/hourslog.kv")


class MyLabelBox(MDBoxLayout):
    title_text = StringProperty("")
    main_text = StringProperty("")
    main_text_opacity = StringProperty("0")
    box_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class HoursLogScreen(MDScreen):
    loggedin_color = (0.745, 0, 0, 1)
    login_state_text = StringProperty("Click to Log Out\n(you are Logged In)")
    logout_state_text = StringProperty("Click to Log In\n(you are Logged Out)")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=False,
        )
        self._excel_output_path = None
        self.menu = None
        create_database()

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
            caller=root.ids.option_button, items=menu_items
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

    def update_loginout_status(self):
        state = current_state()
        if state:
            self.ids.hourslog.text = self.login_state_text
            self.ids.hourslog.md_bg_color = self.loggedin_color
        else:
            self.ids.hourslog.text = self.logout_state_text
            self.ids.hourslog.md_bg_color = self.theme_cls.primary_color

    def on_enter(self):
        self.update_loginout_status()
        self.update_summary_list()
        Clock.schedule_interval(self.update_worked_hours_today, 1)
        last_workday_id = get_last_workday_id()
        if last_workday_id:
            self.update_chips(last_workday_id)

    def on_leave(self):
        Clock.unschedule(self.update_worked_hours_today)

    def update_worked_hours_today(self, dt):
        worked_hours = str(get_worked_hours_today())
        self.ids.worked_hours_today.main_text = worked_hours

    def add_log(self, button):
        # Check the current state and toggle text and color
        if button.text == self.login_state_text:
            button.text = self.logout_state_text
            button.md_bg_color = self.theme_cls.primary_color
            self.set_work_log(False, datetime.now())
        else:
            button.text = self.login_state_text
            button.md_bg_color = self.loggedin_color
            self.set_work_log(True, datetime.now())
        analyze_hours()
        self.update_summary_list()

    def set_work_log(self, checkin: bool, check_time):
        uid = set_work_log(checkin, check_time)
        self.add_check_chip(checkin, check_time.strftime("%H:%M:%S"), uid)

    def update_summary_list(self):
        l_data = get_hourslog_data_summary()
        l_final_data = []
        for data in l_data:
            l_final_data.append(data)
            l_final_data[-1]["hourslogscreen"] = self

        self.ids.hours_summary.data = l_final_data
        self.update_loginout_status()

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
        self.set_work_log(True, check_out_datetime)
        self.update_summary_list()

    def add_checkout(self, instance, value):
        # Convert the date and time to a datetime object
        check_out_datetime = datetime.combine(self._new_date, value)
        # Save the check out time
        print(check_out_datetime)
        self.set_work_log(False, check_out_datetime)
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

    def add_check_chip(self, checkin: bool, check_time: str, uid: int):
        """Aggiunge una nuova chip dinamicamente nella sezione Check-in/Check-out"""
        # Testo dinamico per la chip (esempio: orario di check-in/check-out)
        check_time = "In " + check_time if checkin else "Out " + check_time

        # Aggiungi la chip al container usando il data-binding
        chip = MDChip(
            MDChipText(text=check_time),
            on_release=lambda x: self.show_chip_menu(x),
            id=f"chip_{uid}",
        )
        self.ids.chips_container.add_widget(chip)

    def show_chip_menu(self, instance):
        """Mostra un menu per la chip selezionata"""
        # Logica per mostrare un menu a discesa o azioni sulla chip
        from kivymd.uix.menu import MDDropdownMenu

        menu_items = [
            # {
            #    "text": "Modifica",
            #    "on_release": lambda: self.edit_chip(instance),
            # },
            {
                "text": "Elimina",
                "on_release": lambda: self.remove_chip(instance),
            },
        ]
        menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        )
        menu.open()

    def edit_chip(self, chip):
        """Modifica una chip esistente"""
        chip.text = "Check-in Modificato"

    def remove_chip(self, chip):
        """Rimuove una chip esistente"""
        self.ids.chips_container.remove_widget(chip)
        # Aggiorna il database
        delete_worlkog_entry(int(chip.id.split("_")[1]))
        self.update_summary_list()

    def remove_all_chips(self):
        """Rimuove tutte le chip esistenti"""
        for chip in self.ids.chips_container.children:
            self.ids.chips_container.remove_widget(chip)

    def update_chips(self, worday_id: int):
        """Aggiorna tutte le chip esistenti"""
        l_chips_id = []
        for chip in self.ids.chips_container.children:
            l_chips_id.append(int(chip.id.split("_")[1]))
        l_current_chips_id = get_worklog_data_summary(worday_id)
        for i, log in enumerate(l_current_chips_id):
            if log["uid"] not in l_chips_id:
                self.add_check_chip(
                    log["check_in"], log["timestamp"], log["uid"]
                )
            if i > 20:
                break
        for chip in self.ids.chips_container.children:
            if int(chip.id.split("_")[1]) not in [
                x["uid"] for x in l_current_chips_id
            ]:
                self.ids.chips_container.remove_widget(chip)
