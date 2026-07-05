from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty, NumericProperty
from model import Item
from gui import ItemLayout
from helper import logger
from kivy.metrics import dp


class ItemScrollView(ScrollView):

    dispatcher = ObjectProperty(None)
    item_height = NumericProperty(0)

    def __init__(self, **kwargs):
        super(ItemScrollView, self).__init__(**kwargs)
        self.do_scroll_y = True
        self.do_scroll_x = False
        self.size_hint_min_y = 1

        self.contentGrid = GridLayout(
            cols = 4,
            size_hint_x = 1,
            size_hint_y = None,
            padding = dp(12),
            spacing = dp(12)
        )
        self.contentGrid.bind(
            minimum_height=self.contentGrid.setter('height')
        )
        self.bind(
            height=self._update_item_height
        )

        self.add_widget(self.contentGrid)


    def on_dispatcher(self,instance, dispatcher):
        dispatcher.bind(
            on_login=self.on_login
        )

    def on_login(self, *args, **kwargs):
        self.contentGrid.clear_widgets()
        for item in kwargs.get("items"):
            logger.debug(f"Load Item {item.id}")
            self.contentGrid.add_widget(ItemLayout(item=item, size_hint_y=None, height= self.item_height))

    def _update_item_height(self, *_):
        self.item_height = self.height * 0.7
        for item in self.contentGrid.children:
            item.height = self.item_height




    
            
