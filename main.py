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
