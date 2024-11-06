from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from db.database import (
    add_association,
)  # Ensure this function exists and connects to the database

Builder.load_file("screens/insertion.kv")


class InsertionScreen(Screen):
    def save_association(self, information, character, action, object):
        add_association(
            information=information,
            character_text=character,
            action_text=action,
            object_text=object,
        )
        # Optionally, clear fields after saving
        self.ids.information.text = ""
        self.ids.character.text = ""
        self.ids.action.text = ""
        self.ids.object.text = ""
