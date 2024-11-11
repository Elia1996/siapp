from kivy.lang import Builder
from kivymd.uix.menu import MDDropdownMenu

from kivymd.app import MDApp

KV = """
MDScreen
    md_bg_color: self.theme_cls.backgroundColor

    MDDropdownMenu:
        id: drop_text
        text: "Select item"
        on_release:  print(*args)

"""


class Example(MDApp):
    def open_menu(self, item):
        menu_items = [
            {
                "text": f"{i}",
                "on_release": lambda x=f"Item {i}": self.menu_callback(x),
            }
            for i in range(5)
        ]
        MDDropdownMenu(caller=item, items=menu_items).open()

    def menu_callback(self, text_item):
        self.root.ids.drop_text.text = text_item

    def build(self):
        return Builder.load_string(KV)


Example().run()
