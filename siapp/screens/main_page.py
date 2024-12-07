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
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder

Builder.load_file("siapp/screens/main_page.kv")


class MainPageScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def extract_db(self):
        from siapp.db.models import DATABASE
        from siapp.db.database import get_fmanager_path

        # Copy the database to the user's home directory
        import shutil
        import os

        destpath = os.path.join(get_fmanager_path(), "siapp.db")
        shutil.copy(DATABASE, destpath)
        print("Database copied to", destpath)
        self.ids.db_status.text = f"Database copied to {destpath}"
