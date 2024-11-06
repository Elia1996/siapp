from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from screens.main_menu import MainMenuScreen
from screens.insertion import InsertionScreen
from screens.exercise import ExerciseScreen


class MemoryApp(App):
    def build(self):
        Builder.load_file("screens/main_menu.kv")
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name="main"))
        sm.add_widget(InsertionScreen(name="insertion"))
        sm.add_widget(ExerciseScreen(name="exercise"))
        return sm


if __name__ == "__main__":
    MemoryApp().run()
