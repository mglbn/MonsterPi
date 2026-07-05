from kivy.event import EventDispatcher
from kivy.clock import Clock
from helper import logger
from controller import Controller
from model import User, Item
from gui.widgets.CheckoutModal import CheckoutModal
from gui.LoginTimer import LoginTimer


class CustomDispatcher(EventDispatcher):

    def __init__(self, **kwargs):
        self.loginErrorTimeout = kwargs.pop("loginErrorTimeout", 5) # 5 Sekunden default wert, bestimmt wie lange der Anmeldefehler sichtbar ist.
        self.loginTimeout = kwargs.pop("loginTimeout", 60)
        self.login_timer = LoginTimer()
        self.register_event_type('on_tag')
        self.register_event_type('on_logout')
        self.register_event_type('on_login')
        self.register_event_type('on_login_error')
        self.register_event_type('on_cancel_login_error')
        self.register_event_type('on_BuyButton_release') 
        self.register_event_type('on_CheckoutModal_dismiss')
        self.register_event_type('on_item_bought')
        self.register_event_type('on_timer_reset')
        super(CustomDispatcher, self).__init__(**kwargs)

    def rfidcallback(self, tag: tuple[str, str]):
        text = tag[1]
        tag_id = str(tag[0])
        Clock.schedule_once(lambda dt: self.dispatch('on_tag', tag_id, text))
        

    def on_tag(self, tag_id, text, *args):
        logger.debug(f"Default Eventhandler für 'on_tag' {tag_id}")
        #Login
        if Controller.currentUser == None or Controller.currentUser.tag_id != tag_id:
            self.dispatch('on_logout')
            user: User = Controller.loginUser(tag_id)
            if (user == None):
                self.dispatch('on_login_error')
            else:
                self.dispatch('on_login', user=user, items=Controller.getAllItems4User(user))

            return        

        #bezahle
        if Controller.currentUser != None and Controller.currentUser.tag_id == tag_id and Controller.shoppingCard != None:
            logger.info(f"User mit Tag {tag_id} will bezahlen")
            is_payed = Controller.payForItem(tag_id)
            if is_payed:
                self.dispatch('on_item_bought')
            else:
                self.dispatch('on_item_bought_error')
            return
            
        logger.debug(f"Bekam Tag, aber weder login noch bezahle :/")
        

    def on_logout(self , *args):
        logger.info(f"User wird abgemeldet")
        Controller.logout()
        

    def on_login(self, *args, **kwargs):
        self.login_timer.start_or_reset_login_timer(self.loginTimeout)

    def on_login_error(self, *args, **kwargs):
        logger.debug(f"Zeige Anmeldefehlermeldung für {self.loginErrorTimeout}")
        Clock.schedule_once(lambda dt : self.dispatch('on_cancel_login_error'), self.loginErrorTimeout)
        

    def on_cancel_login_error(self, *args, **kwargs):
        logger.debug("Anmeldefehlermeldung gecancelt")

    def on_BuyButton_release(self, *args, **kwargs):
        item: Item = kwargs.pop('item')
        logger.debug(f"BuyButton von Item {item.id} losgelassen, schedule timeout neu")
        self.login_timer.start_or_reset_login_timer(self.loginTimeout)

        itemIsInShoppingcard: bool = Controller.checkoutItem(item)
        self.modal = CheckoutModal(
            size_hint=(.6,.8),
            item=item,
            pos_hint={'center_x':.5, 'center_y': .5},
            auto_dismiss = True,
            funds= itemIsInShoppingcard

        )
        self.modal.open()
        
    def on_CheckoutModal_dismiss(self, *args, **kwargs):
        logger.debug(f"CheckoutModal dismissed")
        Controller.reset_shoppingcard()
        
    def on_item_bought(self, *args, **kwargs):
        logger.debug("Item erfolgreich gekauft")
        self.login_timer.start_or_reset_login_timer(5)

    def on_timer_reset(self, *args, **kwargs):
        pass   
