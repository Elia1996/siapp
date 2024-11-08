from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from screens.main_menu import MainMenuScreen
from screens.insertion import InsertionScreen
from screens.exercise import ExerciseScreen
from kivy.properties import DictProperty

themes = {
    "light": {
        "background_color": (1, 1, 1, 1),  # White background
        "text_color": (0, 0, 0, 1),  # Black text
        "header_color": (0.3, 0.4, 0.6, 1),  # Light blue
    },
    "dark": {
        "background_color": (0.1, 0.1, 0.1, 1),  # Dark gray background
        "text_color": (1, 1, 1, 1),  # White text
        "header_color": (0.2, 0.2, 0.5, 1),  # Dark blue
    },
}


class MemoryApp(App):
    theme = DictProperty(themes["light"])  # Set default theme

    def build(self):
        Builder.load_file("screens/main_menu.kv")
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name="main"))
        sm.add_widget(InsertionScreen(name="insertion"))
        sm.add_widget(ExerciseScreen(name="exercise"))
        return sm


if __name__ == "__main__":
    MemoryApp().run()
