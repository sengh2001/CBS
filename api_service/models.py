"""Defines all the models used in this application.

__author__ = "Balwinder Sodhi"
__copyright__ = "Copyright 2022"
__license__ = "MIT"
__version__ = "0.1"
__status__ = "Development"
"""

import logging

from peewee import *

from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField

db = PostgresqlExtDatabase('cbs', user='arsh') # Deferred initialization

    
class MediumTextField(TextField):
    field_type = "MEDIUMTEXT"


class MediumBlobField(BlobField):
    field_type = "MEDIUMBLOB"


def create_schema():
    logging.info("Creating DB tables")
    with db:
        db.create_tables(
            [SystemSetting, User, AuditLog, Classroom , Booking]
        )
        logging.info("DB tables created.")


class AuditLog(Model):
    id = AutoField()
    entity_id = BigIntegerField()
    entity_name = CharField(max_length=255)
    old_row_data = JSONField()
    dml_type = CharField(max_length=20)
    dml_timestamp = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    dml_created_by = CharField(max_length=100, null=True)

    class Meta:
        database = db
        only_save_dirty = True
        indexes = (
            # Unique index
            (("entity_id", "entity_name", "dml_type"), True),
        )


class BaseModel(Model):
    id = AutoField()
    is_deleted = BooleanField(constraints=[SQL('DEFAULT FALSE')])
    txn_no = IntegerField(constraints=[SQL('DEFAULT 1')], index=True)
    ins_ts = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    ins_by = CharField(max_length=60, null=True)
    upd_ts = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    upd_by = CharField(max_length=60, null=True)

    class Meta:
        database = db
        only_save_dirty = True


class SystemSetting(BaseModel):
    group = CharField(max_length=60, index=True)
    name = CharField(max_length=200, index=True)
    is_json = BooleanField(index=True)
    value_text = TextField(null=True)
    value_json = JSONField(default={}, null=True)

    class Meta:
        indexes = (
            # Unique index
            (("group", "name", "is_json"), True),
        )


class User(BaseModel):
    email = CharField(max_length=100, unique=True)
    role = CharField(max_length=10)
    org_unit = CharField(max_length=60)
    first_name = CharField(max_length=200, null=True)
    last_name = CharField(max_length=200, null=True)
    is_locked = BooleanField(constraints=[SQL('DEFAULT FALSE')])

    def to_string(self):
        return "{0} {1} ({2})".format(self.first_name, 
            self.last_name, self.email)

class Classroom(BaseModel):
    class_name = CharField(max_length=50, unique=True)
    capacity = IntegerField()
    Location = CharField(max_length=50)
    description = TextField(null=True)
    is_booked = BooleanField(constraints=[SQL('DEFAULT FALSE')])
    is_available = BooleanField(constraints=[SQL('DEFAULT TRUE')])

class Booking(BaseModel):
    classroom = ForeignKeyField(Classroom, backref='bookings')
    user = ForeignKeyField(User, backref='bookings')
    start_time = TimeField()
    end_time = TimeField()
    date = DateField()

    class Meta:
        constraints = [Check('start_time <> end_time')]