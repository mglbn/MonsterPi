"""Testet sync_schema(): neue Model-Felder werden als Spalten nachgezogen,
bestehende Daten und DB-only-Spalten bleiben unberuehrt.

Laeuft gegen in-memory SQLite, dafuer braucht es keinen Postgres.
Ausfuehren: env/Scripts/python.exe tests/test_schema_sync.py
"""
import sys
sys.path.insert(0, 'src')

from peewee import Model, CharField, IntegerField, SqliteDatabase

from model import sync_schema


def check(cond, msg):
    if not cond:
        print(f"FAIL: {msg}")
        sys.exit(1)
    print(f"ok  - {msg}")


db = SqliteDatabase(':memory:')
db.connect()


class UserAlt(Model):
    """Modellstand von frueher: nur name."""
    class Meta:
        database = db
        table_name = 'users'

    name = CharField(null=True)


db.create_tables([UserAlt])
UserAlt.create(name='Marius')


class UserNeu(Model):
    """Neuer Modellstand: plz ist dazugekommen."""
    class Meta:
        database = db
        table_name = 'users'

    name = CharField(null=True)
    plz = IntegerField(null=True)


# 1. Nachziehen des neuen Felds
sync_schema([UserNeu], db)
columns = {c.name for c in db.get_columns('users')}
check('plz' in columns, "neues Feld plz als Spalte nachgezogen")

row = UserNeu.get(UserNeu.name == 'Marius')
check(row.plz is None, "bestehende Daten ueberleben das ALTER")

# 2. Idempotent: zweiter Lauf aendert nichts
sync_schema([UserNeu], db)
check(UserNeu.select().count() == 1, "zweiter Lauf aendert nichts")

# 3. Spalte ohne Model-Feld bleibt stehen
db.execute_sql('ALTER TABLE users ADD COLUMN alt_rest TEXT')
UserNeu.create(name='Test', plz=12345)
sync_schema([UserNeu], db)
columns = {c.name for c in db.get_columns('users')}
check('alt_rest' in columns, "DB-Spalte ohne Model-Feld bleibt unberuehrt")
row = UserNeu.get(UserNeu.name == 'Test')
check(row.plz == 12345, "Werte im neuen Feld lesbar")

print("\nALLE SCHEMA-SYNC-TESTS BESTANDEN")
