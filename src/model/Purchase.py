from .Basemodel import Basemodel
from peewee import *
from model.User import User
from model.Item import Item

class Purchase(Basemodel):
    user = ForeignKeyField(User)
    item = ForeignKeyField(Item)
    price = IntegerField()
    timestamp = TimestampField()