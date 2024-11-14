from datetime import timedelta
from kivymd.uix.screen import MDScreen
from kivymd.uix.filemanager import (
    MDFileManager,
)  # Usa MDFileManager al posto di FileChooserIconView
from kivy.metrics import dp
from plyer import filechooser
from kivy.properties import ListProperty
from kivy.lang import Builder
from kivy.core.text import Label as CoreLabel
from siapp.db.database import (
    add_association,
    get_all_associations,
    get_fmanager_path,
    get_mean_response_time,
)  # Ensure this function exists and connects to the database
from siapp.db.models import create_database
from kivymd.uix.menu import MDDropdownMenu
from siapp.utils.images import path_to_bytes

Builder.load_file("siapp/screens/insertion.kv")


class InsertionScreen(MDScreen):
    info_image_path = ListProperty([])
    pao_image_path = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        create_database()

    def save_association(self):
        add_association(
            information=self.ids.information.text,
            information_image=self.ids.information_image.source,
            character_text=self.ids.character.text,
            pao_image=self.ids.pao_image.source,
            action_text=self.ids.action.text,
            object_text=self.ids.object.text,
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
        print("Getting all associations")
        associations = get_all_associations()

        l_data = []
        print(
            f"Calculating response times for {len(associations)} associations"
        )
        for assoc in associations:
            print(f"Calculating response time for association {assoc.id}")
            mean_response_time = get_mean_response_time(assoc)
            # Convert to timedelta
            if mean_response_time is None:
                mean_response_time = "Nan"
            else:
                mean_response_time = str(timedelta(seconds=mean_response_time))
                # remove hours and minutes
                mean_response_time = ":".join(
                    mean_response_time.split(":")[1:]
                )
                mean_response_time = (
                    mean_response_time.split(".")[0]
                    + "."
                    + mean_response_time.split(".")[1][:3]
                )
            l_data.append(
                {
                    "information_text": assoc.information,
                    "character_text": assoc.character_text,
                    "action_text": assoc.action_text,
                    "object_text": assoc.object_text,
                    "response_time": f"{mean_response_time}",
                    "edit_association": self.edit_association,
                    "association_id": assoc.id,
                    "insertionscreen": self,
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
                    "edit_association": None,
                    "association_id": 0,
                    "insertionscreen": self,
                }
            ]
        self.ids.associations_list.data = l_data

    def calculate_text_height(self, text, font_size=14):
        # Use CoreLabel to calculate the height of the text
        label = CoreLabel(text=text, font_size=font_size)
        label.refresh()  # Refresh to calculate the texture size
        return dp(20)

    def open_filechooser(self, image_type):
        if image_type == "info":
            filechooser.open_file(
                on_selection=self.handle_info_image_selection
            )
        elif image_type == "pao":
            filechooser.open_file(on_selection=self.handle_pao_image_selection)

    def handle_info_image_selection(self, selection):
        self.info_image_path = selection

    def handle_pao_image_selection(self, selection):
        self.pao_image_path = selection

    def on_info_image_path(self, instance, value):
        if value:
            self.ids.information_image.source = value[0]

    def on_pao_image_path(self, instance, value):
        if value:
            self.ids.pao_image.source = value[0]

    def open_edit_menu(self, root):
        """Open the menu to modify the association"""
        menu_items = [
            {
                "text": "Edit",
                "on_release": lambda x="edit": self.edit_menu_callback(
                    x, root
                ),
            },
            {
                "text": "Delete",
                "on_release": lambda x="delete": self.edit_menu_callback(
                    x, root
                ),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=root.ids.option_button_insertion, items=menu_items
        )
        self.menu.open()

    def edit_menu_callback(self, action, root):
        """Trigger the correct action"""
        if action == "edit":
            self.edit_association(root)
        elif action == "delete":
            self.delete_association(root)

    def edit_association(self, root):
        """Edit the association"""
        from siapp.db.database import get_association_by_id

        assoc = get_association_by_id(root.association_id)
        if assoc is None:
            return
        self.ids.information.text = assoc.information
        self.ids.character.text = assoc.character_text
        self.ids.action.text = assoc.action_text
        self.ids.object.text = assoc.object_text
        self.ids.information_image.source = assoc.information_image
        self.ids.pao_image.source = assoc.pao_image
        self.ids.save_association_button.opacity = 0
        self.ids.association_id_label.text = str(assoc.id)
        self.ids.association_id_label.opacity = 1
        self.ids.update_association_button.opacity = 1
        self.ids.cancel_update_button.opacity = 1

    def update_association(self):
        """Update the association"""
        from siapp.db.database import update_association, get_association_by_id

        assoc = get_association_by_id(int(self.ids.association_id_label.text))
        if assoc is None:
            return
        assoc.information = self.ids.information.text
        assoc.character_text = self.ids.character.text
        assoc.action_text = self.ids.action.text
        assoc.object_text = self.ids.object.text
        assoc.information_image = self.ids.information_image.source
        assoc.pao_image = self.ids.pao_image.source
        update_association(assoc)
        self.ids.information.text = ""
        self.ids.character.text = ""
        self.ids.action.text = ""
        self.ids.object.text = ""
        self.ids.information_image.source = ""
        self.ids.pao_image.source = ""

        self.ids.save_association_button.opacity = 1
        self.ids.association_id_label.text = ""
        self.ids.association_id_label.opacity = 0
        self.ids.update_association_button.opacity = 0
        self.ids.cancel_update_button.opacity = 0
        self.refresh_association_list()

    def cancel_update(self):
        """Cancel the update of the association"""
        self.ids.information.text = ""
        self.ids.character.text = ""
        self.ids.action.text = ""
        self.ids.object.text = ""
        self.ids.information_image.source = ""
        self.ids.pao_image.source = ""
        self.ids.save_association_button.opacity = 1
        self.ids.association_id_label.text = ""
        self.ids.association_id_label.opacity = 0
        self.ids.update_association_button.opacity = 0
        self.ids.cancel_update_button.opacity = 0

    def delete_association(self, root):
        """Delete the association"""
        from siapp.db.database import delete_association

        delete_association(root.association_id)
        self.refresh_association_list()
