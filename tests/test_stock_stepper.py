"""Headless-Tests für die Lagerverwaltung (StockScreen).

- StockStepperViewModel: open/nudge/reset/confirm/close, Bestands-Floor 0
- StockViewModel: Artikelliste laden, Aktualisierung nach on_applied
- PurchaseService.all_items/adjust_stock gegen die echten Modelle,
  auf in-memory SQLite umgebunden (kein Postgres nötig)
- SessionViewModel-Integration: show_admin(STOCK_SCREEN) lädt die
  Liste, Rückweg und Logout verwerfen offene Bearbeitungen

Ausführen: env/Scripts/python.exe tests/test_stock_stepper.py
"""
import sys
sys.path.insert(0, 'src')

from peewee import SqliteDatabase

import model
from model import User, Item
import services.purchase
from services.purchase import PurchaseService
from viewmodels import SessionViewModel, StockStepperViewModel, StockViewModel

# --- DB auf in-memory SQLite umlenken (Modelle + PurchaseService-Instanz) ---
test_db = SqliteDatabase(':memory:')
test_db.bind(model.MODELS)
services.purchase.db = test_db
test_db.connect()
test_db.create_tables(model.MODELS, safe=True)


def check(cond, msg):
    if not cond:
        print(f"FAIL: {msg}")
        sys.exit(1)
    print(f"ok  - {msg}")


user_admin = User.create(tag_id='1111', firstname='Admin', lastname='Eins',
                         text='', lastLogon=0, balance=500, dispo=-500, isAdmin=True)
item_voll = Item.create(brand='Monster', flavor='Original', price=100,
                        inStock=5, png=b'')
item_kurz = Item.create(brand='Monster', flavor='Mango', price=150,
                       inStock=2, png=b'')

svc = PurchaseService()

# 1. Service: all_items sortiert
items = svc.all_items()
check([i.flavor for i in items] == ['Mango', 'Original'],
      "all_items: nach Marke/Sorte sortiert")

# 2. Service: adjust_stock lehnt Unsinn ab
check(svc.adjust_stock(item_voll, 0) is False, "adjust_stock: delta 0 -> False")
check(svc.adjust_stock(None, 10) is False, "adjust_stock: kein Artikel -> False")
check(svc.adjust_stock(item_kurz, -10) is False, "adjust_stock: Bestand würde negativ -> False")
check(item_kurz.inStock == 2, "adjust_stock: bei Ablehnung nichts geschrieben")
check(Item.get_by_id(item_kurz.id).inStock == 2, "adjust_stock: DB unberührt")

# 3. Service: gültige Anpassung schreibt und persistiert
check(svc.adjust_stock(item_voll, 5) is True, "adjust_stock: +5 ok")
check(item_voll.inStock == 10, "adjust_stock: Objekt aktualisiert")
check(Item.get_by_id(item_voll.id).inStock == 10, "adjust_stock: in DB persistiert")
svc.adjust_stock(item_voll, -5)   # zurück auf 5

# 4. Stepper: initial hidden, nudge läuft ins Leere
stepper = StockStepperViewModel(svc)
check(stepper.state == 'hidden' and not stepper.confirmable, "Stepper: initial hidden")
stepper.nudge(5)
check(stepper.state == 'hidden', "Stepper: nudge ohne open() ignoriert")

# 5. open(): editing, Delta 0, Bestätigen gesperrt
stepper.open(item_voll)
check(stepper.state == 'editing', "open: Zustand editing")
check(stepper.title == 'Monster Original', "open: Titel mit Marke und Sorte")
check(stepper.delta == 0 and not stepper.confirmable, "open: Delta 0, nicht bestätigbar")
check(stepper.stock_text == '5' and stepper.target_preview == '5',
      "open: Bestand und Vorschau")

# 6. nudge/reset
stepper.nudge(10)
check(stepper.target_preview == '15', "nudge: Vorschau +10")
check(stepper.confirmable, "nudge: bestätigbar")
stepper.nudge(-5)
check(stepper.target_preview == '10', "nudge: mehrfach summieren")
stepper.reset()
check(stepper.delta == 0 and not stepper.confirmable, "reset: Delta zurück, nicht bestätigbar")

# 7. Bestands-Floor: unter 0 steppen
stepper.open(item_kurz)
check(stepper.stock_text == '2', "knapper Artikel: Bestand 2")
stepper.nudge(-5)
check(stepper.target_preview == '-3' and not stepper.confirmable,
      "Floor: Vorschau -3, nicht bestätigbar")
check(stepper.confirm() is False, "Floor: confirm schreibt nicht")
check(stepper.state == 'editing', "Floor: Stepper bleibt offen zur Korrektur")
check(Item.get_by_id(item_kurz.id).inStock == 2, "Floor: nichts in der DB")

# 8. confirm(): schreibt, schließt, feuert on_applied
stepper.open(item_voll)
stepper.nudge(5)
applied = []
stepper.bind(on_applied=lambda s, ok, i: applied.append((ok, i)))
check(stepper.confirm() is True, "confirm: erfolgreich")
check(applied == [(True, item_voll)], "confirm: on_applied(True, item)")
check(stepper.state == 'hidden' and stepper.item is None, "confirm: danach hidden")
check(Item.get_by_id(item_voll.id).inStock == 10, "confirm: +5 persistiert")

# 9. close() verwirft
stepper.open(item_voll)
stepper.nudge(10)
stepper.close()
check(stepper.state == 'hidden' and stepper.delta == 0, "close: verwirft Delta")
check(Item.get_by_id(item_voll.id).inStock == 10, "close: nichts geschrieben")

# 10. StockViewModel: load und Aktualisierung nach on_applied
stock = StockViewModel(PurchaseService(), stepper)
stock.load()
check(len(stock.items) == 2, "StockVM: zwei Artikel geladen")
check(stock.items[0]['name'] == 'Monster Mango' and stock.items[0]['stock_text'] == '2',
      "StockVM: Name und Bestand als Snapshot")
check(stock.items[0]['price_text'] == '1,50 €', "StockVM: Preis formatiert")
check(stock.items[0]['soldout'] is False, "StockVM: Flag soldout False")

stepper.open(stock.items[1]['item'])
stepper.nudge(-5)
stepper.confirm()
check(stock.items[1]['stock_text'] == '5', "StockVM: Liste nach on_applied neu geladen")

# 11. Session-Integration: Menü -> StockScreen -> zurück
svc2 = PurchaseService()
session = SessionViewModel(svc2, login_timeout=30, login_error_timeout=3)
session.on_tag('1111')
check(session.active_screen == 'CheckoutScreen', "Session: Admin eingeloggt")
session.enter_admin()
check(session.active_screen == 'AdminScreen', "Session: Admin-Button führt ins Menü")
check(len(session.stock.items) == 0, "Session: Menü lädt noch keine Artikelliste")

session.show_admin(SessionViewModel.STOCK_SCREEN)
check(session.active_screen == 'StockScreen', "Session: Menü wechselt auf StockScreen")
check(len(session.stock.items) == 2, "Session: Artikelliste beim Betreten geladen")

# Rückweg verwirft offene Bearbeitung
session.stock_stepper.open(svc2.all_items()[0])
session.stock_stepper.nudge(10)
session.back_to_admin_menu()
check(session.active_screen == 'AdminScreen', "Session: zurück im Admin-Menü")
check(session.stock_stepper.state == 'hidden', "Session: Rückweg verwirft offenen Stepper")
check(Item.get_by_id(item_voll.id).inStock == 5, "Session: Rückweg schreibt nichts")

# Offene Bearbeitung beim Logout verwerfen
session.show_admin(SessionViewModel.STOCK_SCREEN)
session.stock_stepper.open(svc2.all_items()[0])
session.stock_stepper.nudge(3)
session.logout()
check(session.active_screen == 'LoginScreen', "Session: Logout funktioniert weiterhin")
check(session.stock_stepper.state == 'hidden', "Session: Logout verwirft offenen Stepper")
check(Item.get_by_id(item_voll.id).inStock == 5, "Session: Logout schreibt nichts")

# Ohne Admin-Flag kein Zugang zum StockScreen
session.show_admin(SessionViewModel.STOCK_SCREEN)
check(session.active_screen == 'LoginScreen', "Session: ohne Admin kein StockScreen")

print("\nALLE LAGER-TESTS BESTANDEN")
