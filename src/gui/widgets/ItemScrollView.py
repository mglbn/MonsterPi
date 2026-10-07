from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty, NumericProperty
from kivy.metrics import dp
from gui.widgets.ItemLayout import ItemLayout


class ItemScrollView(ScrollView):

    items = ObjectProperty(None)
    item_height = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_y = True
        self.do_scroll_x = False
        self.size_hint_min_y = 1

        self.contentGrid = GridLayout(
            cols=4,
            size_hint_x=1,
            size_hint_y=None,
            padding=dp(12),
            spacing=dp(12)
        )
        self.contentGrid.bind(
            minimum_height=self.contentGrid.setter('height')
        )
        self.bind(
            height=self._update_item_height
        )

        self.add_widget(self.contentGrid)

    def on_items(self, instance, items_vm):
        items_vm.bind(items=self._rebuild)

    def _rebuild(self, *_):
        self.contentGrid.clear_widgets()
        for item_vm in self.items.items:
            self.contentGrid.add_widget(
                ItemLayout(item_vm=item_vm, size_hint_y=None, height=self.item_height)
            )

    def _update_item_height(self, *_):
        self.item_height = self.height * 0.7
        for child in self.contentGrid.children:
            child.height = self.item_height
