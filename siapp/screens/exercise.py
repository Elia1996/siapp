import random
from kivy.uix.screenmanager import Screen
from db.database import get_associations
from datetime import datetime


class ExerciseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.associations = []
        self.current_association = None
        self.load_associations()

    def load_associations(self):
        # Carica le prime 20 associazioni ordinate per retention index
        self.associations = get_associations(20)
        random.shuffle(
            self.associations
        )  # Mescola per visualizzare in ordine casuale

    def next_association(self):
        # Passa all'associazione successiva, se disponibile
        if not self.associations:
            self.ids.status.text = (
                "Hai completato tutte le associazioni. Vuoi continuare?"
            )
        else:
            self.current_association = self.associations.pop()
            self.display_association()

    def display_association(self):
        # Mostra l'informazione da memorizzare o il PAO
        assoc = self.current_association
        self.ids.information_label.text = assoc.information
        self.ids.pao_label.text = f"{assoc.character_text} - {assoc.action_text} - {assoc.object_text}"

    def record_response(self, response_type):
        # Registra la risposta dell'utente
        assoc = self.current_association
        assoc.last_repetition_date = datetime.now()
        assoc.refresh_count += 1
        # Esegui l'aggiornamento nel database (puoi aggiornare retention index qui se necessario)
        print(f"Risposta: {response_type}")
        self.next_association()  # Passa alla prossima associazione
