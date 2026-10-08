"""Headless-Tests für den Guthaben-Stepper.

- AmountStepperViewModel: open/nudge/reset/confirm/close, Dispo-Grenze
- AdminViewModel: Userliste laden, Aktualisierung nach on_applied
- PurchaseService.adjust_balance/all_users gegen die echten Modelle,
  auf in-memory SQLite umgebunden (kein Postgres nötig)
- SessionViewModel-Integration: enter_admin lädt die Liste, eigene
  Balance-Anzeige aktualisiert sich nach confirm

Ausführen: env/Scripts/python.exe tests/test_amount_stepper.py
"""
import sys
import time
sys.path.insert(0, 'src')

from peewee import SqliteDatabase

import model
from model import User
import services.purchase
from services.purchase import PurchaseService
from viewmodels import SessionViewModel, AmountStepperViewModel, AdminViewModel

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
user_knapp = User.create(tag_id='2222', firstname='Knapp', lastname='Zwei',
                         text='', lastLogon=0, balance=50, dispo=0, isAdmin=False)

svc = PurchaseService()

# 1. Service: all_users liefert sortierte Liste
users = svc.all_users()
check([u.tag_id for u in users] == ['1111', '2222'], "all_users: nach Nachname sortiert")

# 2. Service: adjust_balance lehnt Unsinn ab
check(svc.adjust_balance(user_admin, 0) is False, "adjust_balance: delta 0 -> False")
check(svc.adjust_balance(None, 100) is False, "adjust_balance: kein User -> False")
check(svc.adjust_balance(user_knapp, -100) is False, "adjust_balance: unter Dispo -> False")
check(user_knapp.balance == 50, "adjust_balance: bei Ablehnung nichts geschrieben")
check(User.get_by_id(user_knapp.id).balance == 50, "adjust_balance: DB unberührt")

# 3. Service: gültige Anpassung schreibt und persistiert
check(svc.adjust_balance(user_admin, 500) is True, "adjust_balance: +5,00 ok")
check(user_admin.balance == 1000, "adjust_balance: Objekt aktualisiert")
check(User.get_by_id(user_admin.id).balance == 1000, "adjust_balance: in DB persistiert")
svc.adjust_balance(user_admin, -500)   # zurück auf 5,00

# 4. Stepper: initial hidden, nudge läuft ins Leere
stepper = AmountStepperViewModel(svc)
check(stepper.state == 'hidden' and not stepper.confirmable, "Stepper: initial hidden")
stepper.nudge(500)
check(stepper.state == 'hidden', "Stepper: nudge ohne open() ignoriert")

# 5. open(): editing, Delta 0, Bestätigen gesperrt
stepper.open(user_admin)
check(stepper.state == 'editing', "open: Zustand editing")
check(stepper.username == 'Admin Eins', "open: Username angezeigt")
check(stepper.delta == 0 and not stepper.confirmable, "open: Delta 0, nicht bestätigbar")
check(stepper.balance_text == '5,00 €' and stepper.target_preview == '5,00 €',
      "open: aktueller Stand und Vorschau")

# 6. nudge/reset
stepper.nudge(500)
check(stepper.target_preview == '10,00 €', "nudge: Vorschau +5,00")
check(stepper.confirmable, "nudge: bestätigbar")
stepper.nudge(100)
check(stepper.target_preview == '11,00 €', "nudge: mehrfach summieren")
stepper.reset()
check(stepper.delta == 0 and not stepper.confirmable, "reset: Delta zurück, nicht bestätigbar")

# 7. Dispo-Grenze: knappes Guthaben unter Dispo steppen
stepper.open(user_knapp)
check(stepper.balance_text == '0,50 €', "knapper User: Stand 0,50")
stepper.nudge(-100)
check(stepper.target_preview == '- 0,50 €' and not stepper.confirmable,
      "Dispo: Vorschau -0,50 unter Dispo 0, nicht bestätigbar")
check(stepper.confirm() is False, "Dispo: confirm schreibt nicht")
check(stepper.state == 'editing', "Dispo: Stepper bleibt offen zur Korrektur")
check(User.get_by_id(user_knapp.id).balance == 50, "Dispo: nichts in der DB")

# 8. confirm(): schreibt, schließt, feuert on_applied
stepper.open(user_admin)
stepper.nudge(500)
applied = []
stepper.bind(on_applied=lambda s, ok, u: applied.append((ok, u)))
check(stepper.confirm() is True, "confirm: erfolgreich")
check(applied == [(True, user_admin)], "confirm: on_applied(True, user)")
check(stepper.state == 'hidden' and stepper.user is None, "confirm: danach hidden")
check(User.get_by_id(user_admin.id).balance == 1000, "confirm: +5,00 persistiert")

# 9. Service lehnt ab, obwohl die Vorschau es zuliess (Dispo hat sich verändert)
stepper.open(user_admin)
stepper.nudge(-500)
check(stepper.confirmable, "race: Vorschau erlaubt -5,00")
user_admin.dispo = 1000   # hinter dem Stepper-Rücken hochgezogen
check(stepper.confirm() is False, "race: Service lehnt ab")
check(applied[-1] == (False, user_admin), "race: on_applied(False, user)")
check(User.get_by_id(user_admin.id).balance == 1000, "race: Balance unverändert")
user_admin.dispo = -500

# 10. close() verwirft
stepper.open(user_admin)
stepper.nudge(1000)
stepper.close()
check(stepper.state == 'hidden' and stepper.delta == 0, "close: verwirft Delta")
check(User.get_by_id(user_admin.id).balance == 1000, "close: nichts geschrieben")

# 11. AdminViewModel: load und Aktualisierung nach on_applied
admin = AdminViewModel(PurchaseService(), stepper)
admin.load()
check(len(admin.users) == 2, "AdminVM: zwei User geladen")
check(admin.users[0]['name'] == 'Admin Eins' and admin.users[0]['balance_text'] == '10,00 €',
      "AdminVM: Name und Balance als Snapshot")
check(admin.users[1]['balance_negative'] is False, "AdminVM: Flag balance_negative")

stepper.open(admin.users[0]['user'])
stepper.nudge(-500)
stepper.confirm()
check(admin.users[0]['balance_text'] == '5,00 €', "AdminVM: Liste nach on_applied neu geladen")

# 12. Session-Integration: enter_admin lädt Liste, eigene Anzeige aktualisiert
svc2 = PurchaseService()
session = SessionViewModel(svc2, login_timeout=30, login_error_timeout=3)
session.on_tag('1111')
check(session.active_screen == 'CheckoutScreen' and session.balance == '5,00 €',
      "Session: Admin eingeloggt, Stand 5,00")
session.enter_admin()
check(session.active_screen == 'AdminScreen', "Session: Admin-Button führt ins Admin-Menü")
check(len(session.admin.users) == 0, "Session: Menü lädt noch keine Userliste")

session.show_admin(SessionViewModel.BALANCE_SCREEN)
check(session.active_screen == 'BalanceScreen', "Session: Menü wechselt auf BalanceScreen")
check(len(session.admin.users) == 2, "Session: Userliste beim Betreten geladen")

# Rückweg ins Menü verwirft einen offenen Stepper
session.stepper.open(svc2.currentUser)
session.stepper.nudge(500)
session.back_to_admin_menu()
check(session.active_screen == 'AdminScreen', "Session: zurück im Admin-Menü")
check(session.stepper.state == 'hidden', "Session: Rückweg verwirft offenen Stepper")
check(User.get_by_id(user_admin.id).balance == 500, "Session: Rückweg schreibt nichts")

session.show_admin(SessionViewModel.BALANCE_SCREEN)
session.stepper.open(svc2.currentUser)
session.stepper.nudge(500)
session.stepper.confirm()
check(session.balance == '10,00 €', "Session: eigene Balance-Anzeige aktualisiert")
check(User.get_by_id(user_admin.id).balance == 1000, "Session: änderung persistiert")
check(session.admin.users[0]['balance_text'] == '10,00 €', "Session: AdminVM-Liste aktuell")

# Logout verwirft einen offenen Stepper
session.stepper.open(svc2.currentUser)
session.stepper.nudge(100)
session.logout()
check(session.active_screen == 'LoginScreen', "Session: Logout funktioniert weiterhin")
check(session.stepper.state == 'hidden', "Session: Logout verwirft offenen Stepper")

# Ohne Admin-Flag kein Zugang zu den Admin-Screens
session.show_admin(SessionViewModel.BALANCE_SCREEN)
check(session.active_screen == 'LoginScreen', "Session: ohne Admin kein BalanceScreen")

print("\nALLE STEPPER-TESTS BESTANDEN")
