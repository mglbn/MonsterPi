from .Item import Item
from .User import User
from .Purchase import Purchase
from .database import db
from helper import logger

MODELS = [
    Item,
    User,
    Purchase
]

def init_db():
    db.connect(reuse_if_open=1)
    db.create_tables(MODELS, safe=True)
    logger.info('Datenbank initiiert')