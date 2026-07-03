from peewee import *
from .database import db
import logging




class Basemodel(Model):
    class Meta:
        database = db

