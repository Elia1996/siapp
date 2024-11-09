import random
from kivymd.uix.screen import MDScreen
from siapp.db.database import (
    get_all_associations,
    calculate_retention_index,
    get_element_number,
    update_association,
)
from datetime import datetime
from kivy.lang import Builder
from enum import Enum


class FlashcardDirection(Enum):
    I_TO_PAO = 1
    P_TO_I = 2
    A_TO_I = 3
    O_TO_I = 4


Builder.load_file("siapp/screens/exercise.kv")


class ExerciseScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.associations = []
        self.current_association = None
        self.bl_direction: FlashcardDirection = None

    def on_enter(self):
        self.load_associations()
        self.next_association()

    def load_associations(self):
        # Load associations ordered by retention index and shuffle them
        self.associations = sorted(
            get_all_associations(), key=lambda x: x.retention_index
        )[:20]
        random.shuffle(self.associations)

    def choose_direction(self) -> bool:
        # Choose the direction of the flashcard
        association = self.current_association
        if association is None:
            return False
        l_possible_directions = []
        if association.character_text is not None:
            l_possible_directions.append(FlashcardDirection.P_TO_I)
        if association.action_text is not None:
            l_possible_directions.append(FlashcardDirection.A_TO_I)
        if association.object_text is not None:
            l_possible_directions.append(FlashcardDirection.O_TO_I)
        if l_possible_directions == []:
            return False
        self.bl_direction = random.choice(l_possible_directions)
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

    def display_association(self):
        # Display the information to be memorized and hide the PAO (Character, Action, Object)
        assoc = self.current_association
        if assoc is None:
            return
        self.ids.information_label.opacity = 0
        self.ids.character_label.opacity = 0
        self.ids.action_label.opacity = 0
        self.ids.object_label.opacity = 0
        self.ids.information_label.text = f"Information: {assoc.information}"
        self.ids.character_label.text = f"Character: {assoc.character_text}"
        self.ids.action_label.text = f"Action: {assoc.action_text}"
        self.ids.object_label.text = f"Object: {assoc.object_text}"
        if self.bl_direction == FlashcardDirection.I_TO_PAO:
            self.ids.information_label.opacity = 1
        elif self.bl_direction == FlashcardDirection.P_TO_I:
            self.ids.character_label.opacity = 1
        elif self.bl_direction == FlashcardDirection.A_TO_I:
            self.ids.action_label.opacity = 1
        elif self.bl_direction == FlashcardDirection.O_TO_I:
            self.ids.object_label.opacity = 1

    def show_solution(self):
        # Make the PAO visible to the user
        if self.current_association is None:
            return
        self._end_time = datetime.now()
        self.ids.information_label.opacity = 1
        self.ids.character_label.opacity = 1
        self.ids.action_label.opacity = 1
        self.ids.object_label.opacity = 1
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
        self.ids.information_label.opacity = 0
        self.ids.character_label.opacity = 0
        self.ids.action_label.opacity = 0
        self.ids.object_label.opacity = 0
        self.next_association()  # Move to the next association
