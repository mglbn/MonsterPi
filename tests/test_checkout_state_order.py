"""Regression-Test fuer die Zuweisungsreihenfolge im CheckoutViewModel.

Der CheckoutModal bindet nur auf state und liest dort synchron title,
hint und hint_color. Die muessen also schon gesetzt sein, bevor state
feuert - sonst ist der Hinweis beim ersten Oeffnen leer und haengt
danach immer einen Zustand hinterher.

Ausfuehren: env/Scripts/python.exe tests/test_checkout_state_order.py
"""
import sys
sys.path.insert(0, 'src')

from viewmodels.checkout_vm import CheckoutViewModel


class FakeItemVM:
    """Minimal-Stub: open() benoetigt nur flavor und price_text."""
    flavor = 'F1'
    price_text = '1,00 €'


def check(cond, msg):
    if not cond:
        print(f"FAIL: {msg}")
        sys.exit(1)
    print(f"ok  - {msg}")


def observer(checkout):
    """Verhalten von CheckoutModal._on_state nachbilden: Sobald state
    feuert, werden title/hint/hint_color gelesen."""
    seen = []
    checkout.bind(state=lambda vm, state: seen.append(
        (state, vm.title, vm.hint, tuple(vm.hint_color))))
    return seen


vm = CheckoutViewModel()
seen = observer(vm)

# 1. Erste Auswahl mit Guthaben -> confirm, Hinweis muss sofort sichtbar sein
vm.open(FakeItemVM(), funds=True)
check(seen[-1] == ('confirm', 'F1 - 1,00 €',
                  CheckoutViewModel.HINT_CONFIRM, (1, 1, 1, 1)),
      "open(confirm): hint/hint_color beim state-Dispatch bereits gesetzt")

# 2. Kauf abgeschlossen -> thanks mit Dank-Hinweis
vm.bought()
check(seen[-1] == ('thanks', 'F1 - 1,00 €',
                  CheckoutViewModel.HINT_THANKS, (.5, 1, .5, 1)),
      "bought(): Danke-Hinweis beim state-Dispatch sichtbar")

# 3. Dialog zu und ohne Guthaben erneut oeffnen -> no_funds mit neuem Hinweis
vm.close()
check(seen[-1] == ('hidden', 'F1 - 1,00 €', CheckoutViewModel.HINT_THANKS, (.5, 1, .5, 1)),
      "close(): state zurueck auf hidden")

vm.open(FakeItemVM(), funds=False)
check(seen[-1] == ('no_funds', 'F1 - 1,00 €',
                  CheckoutViewModel.HINT_NO_FUNDS, (1, .5, .5, 1)),
      "open(no_funds): Hinweis beim state-Dispatch auf no_funds gewechselt")

print("\nALLE CHECKOUT-ORDER-TESTS BESTANDEN")
