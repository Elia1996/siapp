from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from screens.main_menu import MainMenuScreen
from screens.insertion import InsertionScreen
from screens.exercise import ExerciseScreen
from screens.hourslog import HoursLogScreen


class MemoryApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Dark"
        """['Red', 'Pink', 'Purple', 'DeepPurple',
        'Indigo', 'Blue', 'LightBlue', 'Cyan', 'Teal', 'Green',
        'LightGreen', 'Lime', 'Yellow', 'Amber', 'Orange',
        'DeepOrange', 'Brown', 'Gray', 'BlueGray']"""
        self.theme_cls.primary_palette = "LightBlue"
        Builder.load_file("screens/main_menu.kv")
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name="main"))
        sm.add_widget(InsertionScreen(name="insertion"))
        sm.add_widget(ExerciseScreen(name="exercise"))
        sm.add_widget(HoursLogScreen(name="hourslog"))
        return sm


if __name__ == "__main__":
    MemoryApp().run()
