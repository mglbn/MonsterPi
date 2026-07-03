from model import *
from helper import logger
import time
from peewee import JOIN, fn

class AppController():

    def __init__(self):
        self.currentUser: User = None
        self.shoppingCard: Item = None

    def loginUser(self, tag_id) -> User:
        self.currentUser = None
        self.shoppingCard = None
        try:
            self.currentUser = User.get(tag_id=tag_id)
            logger.info(f"User eingeloggt: {self.currentUser}")
        except User.DoesNotExist:
            logger.error(f"User existiert nicht: {tag_id}")
        except:
            logger.error(f"Datenbankfehler")

        return self.currentUser
    
    def thisUserLoggedIn(self, tag_id: int) -> bool:
        return (self.currentUser != None and self.currentUser.tag_id == tag_id)
    
    def reset_shoppingcard(self):
        self.shoppingCard = None
    
    def is_shoppingcard_empty(self):
        return False if self.shoppingCard else True
    
    def checkoutItem(self, item: Item) -> bool:
        sufficientfunds = (self.currentUser.balance - item.price) >= self.currentUser.dispo
        logger.debug(f"User {self.currentUser} hat mittel für Item {item.id}: {sufficientfunds}")
        self.shoppingCard = item if sufficientfunds else None
        #return ob der Nutzer im Hinblick auf sein balance und dispo genug mittel hat
        logger.debug(f"User {self.currentUser} hat Item {self.shoppingCard.id if self.shoppingCard else None} im Warenkorb")
        return sufficientfunds
    
    def payForItem(self, tag_id: int):
        success = True
        if not (self.currentUser and self.shoppingCard):
            logger.error(f"Controllerfehler beim bezahlen: {self.currentUser}, {self.shoppingCard}")
            success = False
            return success

        logger.debug(f"User {self.currentUser.id} möchte Item {self.shoppingCard.id} mit tag {tag_id} bezahlen")
        if (self.shoppingCard.inStock <= 0):
            logger.error(f"Item {self.shoppingCard.id} nicht vorrätig")
            success = False
            return success
        
        # Doch kein Geld?
        if (not ((self.currentUser.balance - self.shoppingCard.price) >= self.currentUser.dispo)):
            logger.error(f"User {self.currentUser} doch kein Geld für {self.shoppingCard}")
            success = False
            return success
        
        self.currentUser.balance -= self.shoppingCard.price
        self.shoppingCard.inStock -= 1
        self.currentUser.save()
        self.shoppingCard.save()
        purchase_entry = Purchase.create(
            user = self.currentUser,
            item = self.shoppingCard,
            price = self.shoppingCard.price,
            timestamp = time.time()
        )
        purchase_entry.save()
        self.currentUser = None
        self.shoppingCard = None
        

        return success
        

        
    def logout(self):
        logger.info(f"Ausgeloggt: {self.currentUser}")
        self.currentUser = None
        self.shoppingCard = None


    
    def getAllItems4User(self, user: User):
        return (Item.select(Item)
            .join(Purchase, JOIN.LEFT_OUTER)
            .join(User, JOIN.LEFT_OUTER)
            .where((User.id == user.id) | (User.id == None))
            .group_by(Item)
            .order_by(fn.COUNT(Item.id).desc())
            )
    
    


Controller = AppController()