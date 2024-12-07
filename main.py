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
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from siapp.screens.main_page import MainPageScreen
from siapp.screens.insertion import InsertionScreen
from siapp.screens.exercise import ExerciseScreen
from siapp.screens.hourslog import HoursLogScreen
from siapp.db.models import create_database
from kivy.utils import platform


def request_permissions():
    if platform == "android":
        from android.permissions import (
            request_permissions,
            check_permission,
            Permission,
        )

        request_permissions(
            [
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
            ]
        )


class MemoryApp(MDApp):
    def on_start(self):
        create_database()

    def build(self):
        self.root = Builder.load_file("main.kv")
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        screen_manager = self.root.ids.screen_manager
        screen_manager.add_widget(MainPageScreen(name="main_page"))
        screen_manager.add_widget(InsertionScreen(name="insertion"))
        screen_manager.add_widget(ExerciseScreen(name="exercise"))
        screen_manager.add_widget(HoursLogScreen(name="hourslog"))
        request_permissions()


if __name__ == "__main__":
    MemoryApp().run()
