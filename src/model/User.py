from .Basemodel import Basemodel
from peewee import *

class User(Basemodel):
    id = IntegerField(primary_key=True)
    tag_id = CharField(unique=True)
    firstname = CharField()
    lastname = CharField()
    text = CharField()
    lastLogon = TimestampField()
    balance = IntegerField()
    dispo = IntegerField()
    # default ist Pflicht, sonst schlägt das schema-sync auf der gefüllten Tabelle fehl
    isAdmin = BooleanField(default=False)

