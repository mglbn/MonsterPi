from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty


class ItemRow(BoxLayout):
    """Zeile der Artikeliste im StockScreen (viewclass der RecycleView).

    Die Daten kommen als Dict aus StockViewModel.items: item (Model),
    name, price_text, stock_text, soldout.
    """

    item = ObjectProperty(None)
    name = StringProperty("")
    price_text = StringProperty("")
    stock_text = StringProperty("")
    soldout = BooleanProperty(False)
