from kivy.uix.screenmanager import Screen
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from db.database import (
    add_association,
    get_all_associations,
)  # Ensure this function exists and connects to the database

Builder.load_file("screens/insertion.kv")


class InsertionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._image_type = None
        self.refresh_association_list()

    def save_association(
        self,
        information,
        character,
        action,
        object,
        information_image,
        pao_image,
    ):
        add_association(
            information=information,
            character_text=character,
            action_text=action,
            object_text=object,
            information_image=information_image,
            pao_image=pao_image,
        )
        # Optionally, clear fields after saving
        self.ids.information.text = ""
        self.ids.character.text = ""
        self.ids.action.text = ""
        self.ids.object.text = ""
        self.ids.information_image.source = None
        self.ids.pao_image.source = None
        self.refresh_association_list()

    def refresh_association_list(self):
        # Refresh the association list in the ExerciseScreen
        associations = get_all_associations()

        l_data = []
        for association in associations:
            l_data.append(
                {
                    "information_text": association.information,
                    "character_text": association.character_text,
                    "action_text": association.action_text,
                    "object_text": association.object_text,
                    "response_time": f"0",
                }
            )
        if l_data == []:
            l_data = [
                {
                    "information_text": "No associations found",
                    "character_text": "",
                    "action_text": "",
                    "object_text": "",
                    "response_time": "",
                }
            ]
        self.ids.associations_list.data = l_data

    def open_filechooser_info(self):
        self.open_filechooser("info")

    def open_filechooser_pao(self):
        self.open_filechooser("character")

    def open_filechooser(self, image_type: str):
        """Open a file chooser popup to select an image file

        Args:
            image_type: the type of image to select (information
                character, action, or object)
        """
        # Create a FileChooser popup to select image files
        content = BoxLayout(orientation="vertical")
        filechooser = FileChooserIconView()
        filechooser.filters = [
            "*.png",
            "*.jpg",
            "*.jpeg",
        ]  # Filter for image files
        self._image_type = image_type
        filechooser.bind(on_submit=self.load_image)

        content.add_widget(filechooser)
        close_btn = Button(text="Close")
        content.add_widget(close_btn)

        self.popup = Popup(
            title="Select an Image", content=content, size_hint=(0.9, 0.9)
        )
        close_btn.bind(on_release=self.popup.dismiss)
        self.popup.open()

    def load_image(self, filechooser, selection, *args):
        if selection and self._image_type == "info":
            self.ids.information_image.source = selection[
                0
            ]  # Set image source to the selected file
            self.popup.dismiss()  # Close the file chooser popup
        elif selection and self._image_type == "pao":
            self.ids.pao_image.source = selection[
                0
            ]  # Set image source to the selected file
            self.popup.dismiss()
