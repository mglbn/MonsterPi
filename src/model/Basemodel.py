from peewee import *
from .database import db




class Basemodel(Model):
    class Meta:
        database = db

