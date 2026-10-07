"""Headless-Tests für die ViewModels (kein Fenster, keine DB nötig).

Ausführen: env/Scripts/python.exe tests/test_viewmodels.py
"""
import sys
sys.path.insert(0, 'src')

from viewmodels import SessionViewModel
from viewmodels.checkout_vm import CheckoutViewModel


class FakeItem:
    def __init__(self, i, price=100, inStock=5):
        self.id = i
        self.brand = 'b'
        self.flavor = f'F{i}'
        self.price = price
        self.inStock = inStock
        self.png = b'png'
    def __repr__(self):
        return f'FakeItem({self.id})'


class FakeUser:
    def __init__(self, tid, balance=500, dispo=-500):
        self.id = int(tid)
        self.tag_id = tid
        self.firstname = 'User' + tid
        self.lastname = 'l'
        self.text = ''
        self.lastLogon = 0
        self.balance = balance
        self.dispo = dispo
    def __repr__(self):
        return f'FakeUser({self.tag_id})'


class FakeService:
    """In-Memory-Fassade der PurchaseService-API."""

    def __init__(self):
        self.users = {'1111': FakeUser('1111'), '2222': FakeUser('2222', balance=50)}
        self.items = [FakeItem(1), FakeItem(2, inStock=1)]
        self.currentUser = None
        self.selectedItem = None

    def login(self, tag_id):
        self.currentUser = None
        self.selectedItem = None
        self.currentUser = self.users.get(tag_id)
        return self.currentUser

    def logout(self):
        self.currentUser = None
        self.selectedItem = None

    def select_item(self, item):
        ok = (self.currentUser.balance - item.price) >= self.currentUser.dispo
        self.selectedItem = item if ok else None
        return ok

    def pay(self, tag_id):
        item = self.selectedItem
        if item is None or item.inStock <= 0:
            return False
        ok = (self.currentUser.balance - item.price) >= self.currentUser.dispo
        if not ok:
            return False
        self.currentUser.balance -= item.price
        item.inStock -= 1
        self.selectedItem = None
        return True

    def items_for_user(self, user):
        return list(self.items)


def check(cond, msg):
    if not cond:
        print(f"FAIL: {msg}")
        sys.exit(1)
    print(f"ok  - {msg}")


svc = FakeService()
session = SessionViewModel(svc, login_timeout=30, login_error_timeout=3)
checkout = session.checkout
items = session.items

# 1. Unbekannter Chip -> Fehleranzeige auf dem LoginScreen
session.on_tag('9999')
check(session.active_screen == 'LoginScreen', "unbekannter Tag: bleibt auf LoginScreen")
check(session.greet == 'Fehler bei Chip: 9999', "unbekannter Tag: Fehleranzeige")
check(tuple(session.greet_color) == (1, 0, 0, 1), "unbekannter Tag: Fehlerfarbe rot")

# 2. Login bekannter Chip -> CheckoutScreen, Daten und Items geladen
session.on_tag('1111')
check(session.active_screen == 'CheckoutScreen', "Login: Screenwechsel zu CheckoutScreen")
check(session.user_logged_in, "Login: user_logged_in gesetzt")
check(session.username == 'User1111', "Login: Username angezeigt")
check(session.balance == '5,00 €', "Login: Balance formatiert")
check(len(items.items) == 2, "Login: Items geladen")
check(checkout.state == 'hidden' and not checkout.is_open, "Login: Checkout-Dialog zu")

# 3. Artikel ohne Betätigung: Balance negativ -> no_funds
session.on_tag('2222')
check(session.username == 'User2222', "Tag-Wechsel: neuer User eingeloggt")
item2 = items.items[1]
item2.item.price = 100
svc.currentUser.dispo = 0
session.select_item(item2)
check(checkout.state == 'no_funds', "Auswahl: no_funds bei zu wenig Guthaben")
check(checkout.is_open, "Auswahl: Dialog offen")
session.on_tag('2222')
check(checkout.state == 'no_funds', "Bezahlversuch ohne Auswahl aendert nichts")
checkout.close()
check(checkout.state == 'hidden' and not checkout.is_open, "close: Dialog wieder zu")
svc.currentUser.dispo = -500

# 4. Normaler Kauf -> thanks, Balance aktualisiert
session.on_tag('1111')
item1 = items.items[0]
session.select_item(item1)
check(checkout.state == 'confirm', "Auswahl: confirm bei ausreichendem Guthaben")
check(checkout.title == 'F1 - 1,00 €', "Auswahl: Titel mit Preis")
session.on_tag('1111')
check(checkout.state == 'thanks', "Bezahlung: thanks nach Kauf")
check(session.balance == '4,00 €', "Bezahlung: Balance aktualisiert")
check(not item1.soldout, "Bezahlung: Bestand 5 -> 4, nicht ausverkauft")

# Kauf des letzten Stuecks -> soldout
item2 = items.items[1]
session.select_item(item2)
session.on_tag('1111')
check(item2.soldout, "Bezahlung: soldout nach letztem Stueck (Bestand 1 -> 0)")

# 5. Anderer Chip waehrend 'thanks' -> Logout + neuer Login, Dialog zu
session.on_tag('2222')
check(checkout.state == 'hidden', "Tag-Wechsel: Checkout-Dialog geschlossen")
check(session.username == 'User2222', "Tag-Wechsel: zweiter User aktiv")
check(svc.currentUser.tag_id == '2222', "Tag-Wechsel: Service-User gewechselt")

# 6. Expliziter Logout -> LoginScreen, Service leer
session.logout()
check(session.active_screen == 'LoginScreen', "Logout: zurueck auf LoginScreen")
check(not session.user_logged_in, "Logout: user_logged_in geloescht")
check(svc.currentUser is None, "Logout: Service-User entfernt")
check(session.username == 'UNBEKANNT', "Logout: Anzeige zurueckgesetzt")
check(session.balance == '0,00 €', "Logout: Balance zurueckgesetzt")

print("\nALLE VM-TESTS BESTANDEN")
