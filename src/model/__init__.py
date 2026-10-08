from .Item import Item
from .User import User
from .Purchase import Purchase
from .database import db
from helper import logger
from playhouse.migrate import SchemaMigrator, migrate

MODELS = [
    Item,
    User,
    Purchase
]

def init_db():
    db.connect(reuse_if_open=1)
    db.create_tables(MODELS, safe=True)
    sync_schema()
    logger.info('Datenbank initiiert')


def sync_schema(models=MODELS, database=db):
    """Neue Model-Felder als Spalten ins Schema nachziehen.

    läuft bei jedem Start: Felder, die am Model dazukommen, werden per
    ALTER TABLE angelegt. Gelöschte oder umbenannte Felder werden
    absichtlich nicht angefasst - eine Spalte ohne Feld bleibt einfach
    stehen, sonst würden wir beim Start Kundendaten wegwerfen.

    Achtung: neue Felder brauchen null=True oder default=..., sonst
    schlägt das ALTER auf Tabellen mit Daten fehl.
    """
    migrator = SchemaMigrator.from_database(database)
    for model in models:
        table = model._meta.table_name
        existing = {column.name for column in database.get_columns(table)}
        for field in model._meta.sorted_fields:
            if field.column_name in existing:
                continue
            try:
                migrate(migrator.add_column(table, field.column_name, field))
                logger.info(f'Schema: {table}.{field.column_name} angelegt')
            except Exception as e:
                logger.error(f'Schema: {table}.{field.column_name} fehlgeschlagen: {e}')
        field_columns = {field.column_name for field in model._meta.sorted_fields}
        for name in sorted(existing - field_columns):
            logger.info(f'Schema: {table}.{name} ohne Model-Feld, bleibt stehen')