from .Basemodel import Basemodel
from peewee import *

class Item(Basemodel):
    id = IntegerField(primary_key=True)
    brand = CharField()
    flavor = CharField()
    price = IntegerField() # in cent
    inStock = IntegerField()
    png = BlobField()


    