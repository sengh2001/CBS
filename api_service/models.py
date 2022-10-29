"""Defines all the models used in this application.

__author__ = "Balwinder Sodhi"
__copyright__ = "Copyright 2022"
__license__ = "MIT"
__version__ = "0.1"
__status__ = "Development"
"""

from email.policy import default
import logging
from datetime import datetime as DT

from peewee import *
from playhouse.mysql_ext import JSONField

# Deferred initialization
db = MySQLDatabase(None)
    
class MediumTextField(TextField):
    field_type = "MEDIUMTEXT"


class MediumBlobField(BlobField):
    field_type = "MEDIUMBLOB"


def create_schema():
    logging.info("Creating DB tables")
    with db:
        db.create_tables(
            [User, RolePermission, SystemSetting, UserProfile,
            LeaveApplication, LeaveRule, VacationPeriod,
            AdminDutyCredit, ResearchCredit, AdminActivity, ResearchActivity,
            WorkRequest, FormAction, HolidayInfo, AuditLog]
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
    first_name = CharField(max_length=200, null=True)
    last_name = CharField(max_length=200, null=True)
    is_locked = BooleanField(constraints=[SQL('DEFAULT FALSE')])

    def to_string(self):
        return "{0} {1} ({2})".format(self.first_name, 
            self.last_name, self.email)


class RolePermission(BaseModel):
    role = CharField(max_length=40, index=True)
    perm = CharField(max_length=100, index=True)
    description = CharField(max_length=150, null=True)

    class Meta:
        indexes = (
            # Unique index
            (("role", "perm"), True),
        )


class UserProfile(BaseModel):
    user = ForeignKeyField(User, backref="profiles")
    gender = CharField(max_length=10, constraints=[SQL("DEFAULT 'M'")])
    dob = DateField()
    doj = DateField(default=DT.now().date)
    category = CharField(max_length=10, null=True)
    basic_pay = IntegerField(default=0)
    cpc_level = CharField(max_length=10, null=True)
    area = CharField(max_length=150)
    valid_from = DateField(default=DT.now().date)
    valid_till = DateField(null=True)
    allowed_compoff = BooleanField(constraints=[SQL('DEFAULT FALSE')])

    class Meta:
        indexes = (
            # Unique index
            (("user", "valid_from", "valid_till",), True),
        )


class LeaveRule(BaseModel):
    sub_role = CharField(max_length=10)
    leave_type = CharField(max_length=40)
    yearly_quota = IntegerField()
    max_per_instance = IntegerField()
    max_accrual = IntegerField(constraints=[SQL('DEFAULT 0')])
    min_service_years = IntegerField(constraints=[SQL('DEFAULT 0')])
    rolls_over = BooleanField(constraints=[SQL('DEFAULT FALSE')])
    encashable = BooleanField(constraints=[SQL('DEFAULT FALSE')])
    fraction_allowed = BooleanField(constraints=[SQL('DEFAULT FALSE')])
    conversion_to_el = FloatField(constraints=[SQL('DEFAULT 0')])
    valid_from = DateField()
    valid_till = DateField(null=True)
    rec_role = CharField(max_length=10, null=True)
    apr_role = CharField(max_length=10, constraints=[SQL("DEFAULT 'HOD'")])
    match_area = BooleanField(constraints=[SQL('DEFAULT FALSE')])
    
    class Meta:
        indexes = (
            # Unique index
            (("sub_role", "leave_type", "valid_from"), True),
        )


class VacationPeriod(BaseModel):
    year = IntegerField()
    start_dt = DateField()
    end_dt = DateField()
    
    class Meta:
        indexes = (
            # Unique index
            (("year", "start_dt", "end_dt",), True),
        )


class LeaveApplication(BaseModel):
    user = ForeignKeyField(User, backref="leaves")
    leave_type = CharField(max_length=40)
    leaving_stn = BooleanField(default=False)
    start_dt = DateField()
    end_dt = DateField()
    status = CharField(max_length=40)
    leave_phone = CharField(max_length=20)
    leave_addr = TextField()
    applicant_notes = TextField()
    approver_notes = TextField(null=True)
    reco_notes = TextField(null=True)
    fn_an = CharField(max_length=4, default="NA")

    class Meta:
        constraints = [Check('start_dt <= end_dt')]
        indexes = (
            # Unique index
            (("user", "start_dt", "status",), True),
            (("user", "end_dt", "status",), True),
        )


class AdminDutyCredit(BaseModel):
    work_type = CharField(max_length=200)
    credits = IntegerField()
    status = CharField(max_length=40)
    valid_from = DateField()
    valid_till = DateField(null=True)
    
    def to_string(self):
        return "{0} (Cr. {1})".format(self.work_type, self.credits)
    
    class Meta:
        indexes = (
            # Unique index
            (("work_type", "valid_from", "valid_till",), True),
        )


class ResearchCredit(BaseModel):
    classif = CharField(max_length=200)
    pub_type = CharField(max_length=200)
    credits = IntegerField()
    status = CharField(max_length=40)
    valid_from = DateField()
    valid_till = DateField(null=True)

    def to_string(self):
        return "{0} ({1}, Cr. {2})".\
            format(self.classif, self.pub_type, self.credits)

    class Meta:
        indexes = (
            # Unique index
            (("classif", "pub_type", "valid_from", "valid_till",), True),
        )


class AdminActivity(BaseModel):
    user = ForeignKeyField(User, backref="admin_activities")
    credit = ForeignKeyField(AdminDutyCredit, backref="credit_actitivies")
    credit_override = IntegerField(null=True)
    status = CharField(max_length=40, default="DRA")
    start_dt = DateField()
    end_dt = DateField(null=True)

    class Meta:
        indexes = (
            # Unique index
            (("user", "credit", "start_dt",), True),
        )


class ResearchActivity(BaseModel):
    user = ForeignKeyField(User, backref="research_activities")
    credit = ForeignKeyField(ResearchCredit, backref="credit_actitivies")
    credit_override = IntegerField(null=True)
    status = CharField(max_length=40, default="DRA")
    title = CharField(max_length=255)
    authors = TextField()
    pub_name = TextField()
    pub_dt = DateField(null=True)
    # A = Accepted, P = Published
    pub_status = CharField(max_length=2)
    doi = CharField(max_length=255, null=True, unique=True)

    class Meta:
        indexes = (
            # Unique index
            (("user", "credit", "title", "pub_dt"), True),
        )


class WorkRequest(BaseModel):
    user = ForeignKeyField(User, backref="work_requests")
    status = CharField(max_length=40)
    start_dt = DateField()
    end_dt = DateField()
    reasons = TextField()
    approver_notes = TextField(null=True)

    class Meta:
        indexes = (
            # Unique index
            (("user", "start_dt",), True),
        )


class HolidayInfo(BaseModel):
    start_dt = DateField()
    end_dt = DateField()
    period_type = CharField(max_length=10)
    description = CharField(max_length=250)
    
    class Meta:
        indexes = (
            # Unique index
            (("start_dt", "end_dt",), True),
        )


class FormAction(BaseModel):
    form = CharField(max_length=100)
    user_role = CharField(max_length=10)
    status_now = CharField(max_length=40)
    action = CharField(max_length=60)
    status_after = CharField(max_length=40, null=True)
    match_area = BooleanField(constraints=[SQL('DEFAULT TRUE')])

    class Meta:
        indexes = (
            # Unique index
            (("form", "status_now", "user_role", "action"), True),
        )

