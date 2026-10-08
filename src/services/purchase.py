import time
from peewee import JOIN, fn
from model import User, Item, Purchase, db
from helper import logger


class PurchaseService():
    """Kivy-freie Kauf- und Anmelde-Logik.

    Hält den Domänen-Zustand (aktueller User, ausgewähltes Item) und
    kapselt alle DB-Zugriffe. Keine Imports aus gui/ oder viewmodels/.
    """

    def __init__(self):
        self.currentUser: User = None
        self.selectedItem: Item = None

    def login(self, tag_id) -> User:
        self.currentUser = None
        self.selectedItem = None
        try:
            self.currentUser = User.get(tag_id=tag_id)
            # letzten Login festhalten
            self.currentUser.lastLogon = time.time()
            self.currentUser.save()
            logger.info(f"User eingeloggt: {self.currentUser}")
        except User.DoesNotExist:
            logger.error(f"User existiert nicht: {tag_id}")
        except:
            logger.error(f"Datenbankfehler")

        return self.currentUser

    def logout(self):
        logger.info(f"Ausgeloggt: {self.currentUser}")
        self.currentUser = None
        self.selectedItem = None

    def select_item(self, item: Item) -> bool:
        sufficientfunds = (self.currentUser.balance - item.price) >= self.currentUser.dispo
        logger.debug(f"User {self.currentUser} hat mittel für Item {item.id}: {sufficientfunds}")
        self.selectedItem = item if sufficientfunds else None
        #return ob der Nutzer im Hinblick auf sein balance und dispo genug mittel hat
        logger.debug(f"User {self.currentUser} hat Item {self.selectedItem.id if self.selectedItem else None} im Warenkorb")
        return sufficientfunds

    def pay(self, tag_id: int) -> bool:
        success = True
        if not (self.currentUser and self.selectedItem):
            logger.error(f"Controllerfehler beim bezahlen: {self.currentUser}, {self.selectedItem}")
            success = False
            return success

        logger.debug(f"User {self.currentUser.id} möchte Item {self.selectedItem.id} mit tag {tag_id} bezahlen")
        if (self.selectedItem.inStock <= 0):
            logger.error(f"Item {self.selectedItem.id} nicht vorrätig")
            success = False
            return success

        # Doch kein Geld?
        if (not ((self.currentUser.balance - self.selectedItem.price) >= self.currentUser.dispo)):
            logger.error(f"User {self.currentUser} doch kein Geld für {self.selectedItem}")
            success = False
            return success

        with db.atomic():
            self.currentUser.balance -= self.selectedItem.price
            self.selectedItem.inStock -= 1
            self.currentUser.save()
            self.selectedItem.save()
            purchase_entry = Purchase.create(
                user = self.currentUser,
                item = self.selectedItem,
                price = self.selectedItem.price,
                timestamp = time.time()
            )

        self.selectedItem = None
        return success

    def all_items(self):
        return list(Item.select().order_by(Item.brand, Item.flavor))

    def adjust_stock(self, item: Item, delta: int) -> bool:
        """Bestand eines Artikels um delta verändern, transaktional.

        Gibt False zurück, wenn kein Artikel, kein Delta oder der
        neue Bestand negativ wäre - dann wird nichts geschrieben.
        """
        if item is None or delta == 0:
            return False

        neu = item.inStock + delta
        if neu < 0:
            logger.error(f"Bestand würde negativ: {item} um {delta} auf {neu}")
            return False

        with db.atomic():
            item.inStock = neu
            item.save()

        logger.info(f"Bestand angepasst: {item} um {delta} auf {neu}")
        return True

    def all_users(self):
        return list(User.select().order_by(User.lastname, User.firstname))

    def adjust_balance(self, user: User, delta: int) -> bool:
        """Guthaben eines Users um delta (Cent) ändern, transaktional.

        Gibt False zurück, wenn kein User, kein Betrag oder der neue
        Stand unter dem Dispo läge - dann wird nichts geschrieben.
        """
        if user is None or delta == 0:
            return False

        neu = user.balance + delta
        if neu < user.dispo:
            logger.error(f"Dispo würde unterschritten: {user} um {delta} auf {neu}")
            return False

        with db.atomic():
            user.balance = neu
            user.save()

        logger.info(f"Balance angepasst: {user} um {delta} auf {neu}")
        return True

    def items_for_user(self, user: User):
        return (Item.select(Item)
            .join(Purchase, JOIN.LEFT_OUTER, on=
                  (Purchase.item == Item.id) &
                  (Purchase.user == user.id)
                  )
            .group_by(Item)
            .order_by(fn.COUNT(Purchase.id).desc())
            )
