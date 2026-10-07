"""Testet den Aktivitaets-Reset: jede Touch-Eingabe startet den
laufenden Logout-Timer neu (SessionViewModel.notify_activity).

Das Window-Binding selbst ist App-Geschichte; hier wird nur das
Verhalten des ViewModels geprueft - dafuer reicht ein Fake-Service,
Clock laeuft headless nicht, wir schauen auf die geplanten Events.

Ausfuehren: env/Scripts/python.exe tests/test_activity_timer.py
"""
import sys
sys.path.insert(0, 'src')

from viewmodels import SessionViewModel


class FakeUser:
    tag_id = '1111'
    firstname = 'User1111'
    balance = 500
    dispo = -500


class FakeItem:
    inStock = 5


class FakeItemVM:
    item = FakeItem()
    flavor = 'F1'
    price_text = '1,00 €'

    def refresh_stock(self):
        pass


class FakeService:
    def __init__(self):
        self.currentUser = None
        self.selectedItem = None

    def login(self, tag_id):
        self.currentUser = FakeUser() if tag_id == '1111' else None
        return self.currentUser

    def logout(self):
        self.currentUser = None
        self.selectedItem = None

    def select_item(self, item):
        self.selectedItem = item
        return True

    def pay(self, tag_id):
        self.selectedItem = None
        return True

    def items_for_user(self, user):
        return []


def check(cond, msg):
    if not cond:
        print(f"FAIL: {msg}")
        sys.exit(1)
    print(f"ok  - {msg}")


session = SessionViewModel(FakeService(), login_timeout=30, login_error_timeout=3)

# 1. Ohne Login laeuft kein Timer -> notify_activity ist ein No-Op
session.notify_activity()
check(session._logout_event is None, "vor Login: kein Timer, kein Fehler")

# 2. Login armiert den Timer
session.on_tag('1111')
timer_vorher = session._logout_event
check(timer_vorher is not None, "Login: Logout-Timer gesetzt")

# 3. Fortschritt laeuft etwas hoch, dann Touch: Timer neu, Fortschritt auf 0
session._tick_progress(3)
check(session.logout_progress > 0, "Fortschritt laeuft")
session.notify_activity()
check(session._logout_event is not None and session._logout_event is not timer_vorher,
      "Touch: altes Event verworfen, neues gesetzt")
check(session.logout_progress == 0, "Touch: Fortschritt wieder bei 0")
check(session._progress_duration == 30, "Touch: Dauer unveraendert (30s)")

# 4. Nach Kauf laeuft der 5s-Timer - auch den startet ein Touch neu
session.select_item(FakeItemVM())
session.on_tag('1111')   # bezahlen -> _start_login_timer(5)
check(session._progress_duration == 5, "Kauf: 5s-Timer aktiv")
timer_vorher = session._logout_event
session.notify_activity()
check(session._logout_event is not timer_vorher, "Touch im Danke-Zustand: Timer neu")

# 5. Logout ruemt auf, notify_activity greift danach ins Leere
session.logout()
check(session._logout_event is None, "Logout: Timer weg")
session.notify_activity()
check(session._logout_event is None, "nach Logout: Touch bleibt No-Op")

print("\nALLE TIMER-TESTS BESTANDEN")
