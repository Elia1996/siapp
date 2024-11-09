from datetime import timedelta
from kivymd.uix.screen import MDScreen
from kivymd.uix.filemanager import (
    MDFileManager,
)  # Usa MDFileManager al posto di FileChooserIconView
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.core.text import Label as CoreLabel
from siapp.db.database import (
    add_association,
    get_all_associations,
    get_mean_response_time,
)  # Ensure this function exists and connects to the database

Builder.load_file("siapp/screens/insertion.kv")


class InsertionScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._image_type = None
        self.file_manager = MDFileManager(
            exit_manager=self.close_filechooser, select_path=self.load_image
        )
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
        self.ids.information_image.source = ""
        self.ids.pao_image.source = ""
        self.refresh_association_list()

    def refresh_association_list(self):
        # Refresh the association list in the ExerciseScreen
        associations = get_all_associations()

        l_data = []
        for assoc in associations:
            max_height = max(
                self.calculate_text_height(assoc.information),
                self.calculate_text_height(assoc.character_text),
                self.calculate_text_height(assoc.action_text),
                self.calculate_text_height(assoc.object_text),
            )
            mean_response_time = get_mean_response_time(assoc)
            # Convert to timedelta
            if mean_response_time is None:
                mean_response_time = "Nan"
            else:
                mean_response_time = timedelta(
                    seconds=int(mean_response_time), microseconds=0
                )
            print(mean_response_time)
            l_data.append(
                {
                    "information_text": assoc.information,
                    "character_text": assoc.character_text,
                    "action_text": assoc.action_text,
                    "object_text": assoc.object_text,
                    "response_time": f"{mean_response_time}",
                    "height": max_height,
                    "edit_association": self.edit_association,
                    "association_id": assoc.id,
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
                    "height": 0,
                    "edit_association": None,
                    "association_id": 0,
                }
            ]
        self.ids.associations_list.data = l_data

    def edit_association(self, association):
        pass

    def calculate_text_height(self, text, font_size=14):
        # Use CoreLabel to calculate the height of the text
        label = CoreLabel(text=text, font_size=font_size)
        label.refresh()  # Refresh to calculate the texture size
        return dp(20)

    def open_filechooser_info(self):
        self.open_filechooser("info")

    def open_filechooser_pao(self):
        self.open_filechooser("pao")

    def open_filechooser(self, image_type: str):
        """Open a file chooser to select an image file.

        Args:
            image_type: the type of image to select (information
                or pao)
        """
        self._image_type = image_type
        self.file_manager.show(
            "/"
        )  # Opens file manager at root or specific path

    def close_filechooser(self, *args):
        """Close the file chooser."""
        self.file_manager.close()

    def load_image(self, path):
        """Load the selected image from the file chooser."""
        if path:
            if self._image_type == "info":
                self.ids.information_image.source = (
                    path  # Set image source for information
                )
            elif self._image_type == "pao":
                self.ids.pao_image.source = path  # Set image source for pao
            self.close_filechooser()  # Close the file chooser
