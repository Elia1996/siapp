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
import random
from typing import Optional
from kivymd.uix.screen import MDScreen
from siapp.db.database import (
    get_all_associations,
    calculate_retention_index,
    get_element_number,
    update_association,
)
from siapp.db.models import Association
from datetime import datetime
from kivy.lang import Builder
from enum import Enum


class FlashcardDirection(Enum):
    I_TO_PAO = 1
    P_TO_I = 2
    A_TO_I = 3
    O_TO_I = 4


Builder.load_file("siapp/screens/exercise.kv")

from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, ListProperty


class ExerciseScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.associations = []
        self.current_association = None
        self.bl_direction: FlashcardDirection = None

    def on_enter(self):
        calculate_retention_index()
        self.load_associations()
        self.next_association()

    def load_associations(self):
        # Load associations ordered by retention index and shuffle them
        self.associations = sorted(
            get_all_associations(),
            key=lambda x: x.retention_index,
            reverse=True,
        )
        from siapp.db.models import Association

        assoc: Association
        for assoc in self.associations:
            print(f"id: {assoc.id}, retention: {assoc.retention_index}")

    def choose_direction(self) -> bool:
        # Choose the direction of the flashcard
        assoc: Association = self.current_association
        d_ass = {
            FlashcardDirection.I_TO_PAO: assoc.last_response_time_I_to_PAO,
            FlashcardDirection.P_TO_I: assoc.last_response_time_P_to_I,
            FlashcardDirection.A_TO_I: assoc.last_response_time_A_to_I,
            FlashcardDirection.O_TO_I: assoc.last_response_time_O_to_I,
        }
        max_resp_time = 0
        for direction, resptime in d_ass.items():
            if resptime is None:
                self.bl_direction = direction
                break
            if resptime > max_resp_time:
                max_resp_time = resptime
                self.bl_direction = direction

        return True

    def next_association(self):
        # Move to the next association if available
        if not self.associations:
            if get_element_number() == 0:
                self.ids.information_label.text = "No associations available"
                return
            calculate_retention_index()
            self.load_associations()
            self.next_association()
        else:
            self.current_association = self.associations.pop()
            self._start_time = datetime.now()
            ret = self.choose_direction()
            self.display_association()

    def remove_information_card(self):
        # Remove the character card from the flashcard
        self.ids.information_image_card.opacity = 0

    def remove_pao_card(self):
        # Remove the PAO card from the flashcard
        self.ids.pao_image_card.opacity = 0

    def add_information_image(self, image: Optional[bytes]):
        # Add the infromation image to the flashcard
        card = self.ids.information_image_card
        if image is None:
            card.opacity = 0
        else:
            card.opacity = 1
            self.ids.information_image.source = image

    def add_pao_images(self, image: Optional[bytes]):
        # Add the PAO image to the flashcard
        card = self.ids.pao_image_card
        if image is None:
            card.opacity = 0
        else:
            card.opacity = 1
            self.ids.pao_image.source = image

    def display_association(self):
        # Display the information to be memorized and hide the PAO (Character, Action, Object)
        assoc = self.current_association
        if assoc is None:
            return
        self.ids.information_label.main_text_opacity = "0"
        self.ids.character_label.main_text_opacity = "0"
        self.ids.action_label.main_text_opacity = "0"
        self.ids.object_label.main_text_opacity = "0"
        self.ids.information_image_card.opacity = 0
        self.ids.pao_image_card.opacity = 0
        self.ids.information_label.main_text = f"{assoc.information}"
        self.ids.character_label.main_text = f"{assoc.character_text}"
        self.ids.action_label.main_text = f"{assoc.action_text}"
        self.ids.object_label.main_text = f"{assoc.object_text}"
        if self.bl_direction == FlashcardDirection.I_TO_PAO:
            self.ids.information_label.main_text_opacity = "1"
            self.add_information_image(
                self.current_association.information_image
            )
        elif self.bl_direction == FlashcardDirection.P_TO_I:
            self.ids.character_label.main_text_opacity = "1"
            self.add_pao_images(self.current_association.pao_image)
        elif self.bl_direction == FlashcardDirection.A_TO_I:
            self.ids.action_label.main_text_opacity = "1"
            self.add_pao_images(self.current_association.pao_image)
        elif self.bl_direction == FlashcardDirection.O_TO_I:
            self.ids.object_label.main_text_opacity = "1"
            self.add_pao_images(self.current_association.pao_image)

    def show_solution(self):
        # Make the PAO visible to the user
        if self.current_association is None:
            return
        self._end_time = datetime.now()
        self.ids.information_label.main_text_opacity = "1"
        self.ids.character_label.main_text_opacity = "1"
        self.ids.action_label.main_text_opacity = "1"
        self.ids.object_label.main_text_opacity = "1"
        self.add_information_image(self.current_association.information_image)
        self.add_pao_images(self.current_association.pao_image)
        elapsed_time = self._end_time - self._start_time
        elapsed_time = elapsed_time.total_seconds()
        if self.bl_direction == FlashcardDirection.I_TO_PAO:
            self.current_association.last_response_time_I_to_PAO = elapsed_time
        elif self.bl_direction == FlashcardDirection.P_TO_I:
            self.current_association.last_response_time_P_to_I = elapsed_time
        elif self.bl_direction == FlashcardDirection.A_TO_I:
            self.current_association.last_response_time_A_to_I = elapsed_time
        elif self.bl_direction == FlashcardDirection.O_TO_I:
            self.current_association.last_response_time_O_to_I = elapsed_time
        self.current_association.refresh_count += 1
        self.current_association.last_repetition_date = datetime.now()
        self.ids.right_button.disabled = False
        self.ids.wrong_button.disabled = False
        self.ids.difficult_button.disabled = False
        self.ids.show_solution_button.disabled = True

    def record_response(self, response_type):
        # Record the user’s response (right, wrong, or difficult)
        if self.current_association is None:
            return
        if response_type == "right":
            if self.current_association.difficulty > 0:
                self.current_association.difficulty -= 0.5
            if self.current_association.difficulty < 0:
                self.current_association.difficulty = 0
        elif response_type == "wrong":
            self.current_association.difficulty += 1
        elif response_type == "difficult":
            self.current_association.difficulty += 0.5
        update_association(self.current_association)
        self.ids.information_label.main_text_opacity = "0"
        self.ids.character_label.main_text_opacity = "0"
        self.ids.action_label.main_text_opacity = "0"
        self.ids.object_label.main_text_opacity = "0"
        self.remove_information_card()
        self.remove_pao_card()
        self.ids.show_solution_button.disabled = False
        self.ids.right_button.disabled = True
        self.ids.wrong_button.disabled = True
        self.ids.difficult_button.disabled = True
        self.next_association()  # Move to the next association
