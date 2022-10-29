"""View functions for managing the API.

__author__ = "Balwinder Sodhi"
__copyright__ = "Copyright 2022"
__license__ = "MIT"
__version__ = "0.1"
__status__ = "Development"
"""

from datetime import timedelta
import uuid
from flask import request
from werkzeug.utils import secure_filename
from views_common import *

def _check_wr_access(user_id:int):
    cu = session_user()
    myRole, myArea = cu["role"], cu["area"]
    if cu["id"] == user_id or is_user_in_role(["SUP", "DIR"]):
        return
    uobj = User.get_by_id(user_id)
    upr = get_current_profile(uobj)
    if not (myRole in ["HOD", "MGR"] and myArea == upr.area):
        raise AppException("Cannot access information!")


def _check_access(user_id:int, leave_type:str = None):
    cu = session_user()
    myrole = cu["role"]
    if cu["id"] == user_id or is_user_in_role(["SUP"]):
        return
    uobj = User.get_by_id(user_id)
    upr = get_current_profile(uobj)

    lrq = LeaveRule.select()
    lrq = lrq.where(LeaveRule.sub_role == uobj.role)
    if leave_type:
        lrq = lrq.where(LeaveRule.leave_type == leave_type)
    lrq = lrq.where(LeaveRule.valid_from <= DT.now())
    lrq = lrq.where((LeaveRule.rec_role == myrole) |
                    (LeaveRule.apr_role == myrole))
    lrq = lrq.where((LeaveRule.valid_till.is_null()) |
                (LeaveRule.valid_till >= DT.now()))
    
    if not lrq.exists():
        raise AppException("Required leave rule setup incomplete. Please contact support.")
    if (lrq[0].match_area and cu["area"] != upr.area):
        raise AppException("You are not allowed to access/change this data!")


def _check_request_status(old_status, new_status, start_dt):
    dt = DT.strptime(start_dt, "%Y-%m-%d") if isinstance(start_dt, str) else start_dt
    faq = FormAction.select().where(FormAction.status_after == new_status)
    faq = faq.where(FormAction.status_now.in_([old_status, "ANY"]))
    faq = faq.where(FormAction.user_role.in_(["ANY", current_role()]))
    
    if not faq.exists():
        raise AppException("Change not allowed.")
    
    if not is_user_in_role("SUP") and \
        (old_status in ["APP", "REJ", "COM"]) and (DT.now() > dt):
        raise AppException("Change not allowed. Please contact IT support to override.")


def _save_uploaded_file(dataFile, dataType):
    if dataFile.filename == '':
        raise AppException("Please select the data file. No file supplied!")
    orig_fn = secure_filename(dataFile.filename)
    filename = "DAT_{0}_{1}_._{2}".format(dataType, uuid.uuid4(), orig_fn)
    file_path = os.path.join(get_upload_folder(), filename)
    dataFile.save(file_path)
    return file_path, filename


@auth_check(roles=["SUP"])
def data_import():
    try:
        dataType = request.form.get('dataType')
        dataFile = request.files['dataFile']
        file_path, fn = _save_uploaded_file(dataFile, dataType)
        rows = 0
        # if dataType == "TAX":
        #     rows = taxonomy_import(file_path)
        # elif dataType == "OBK":
        #     rows = books_import(file_path, False)
        # else:
        #     return error_json("Invalid data type {}".format(dataType))
        
        return ok_json("Imported {0} data records.".format(rows))

    except Exception as ex:
        msg = "Error when importing data. Cause: {}".format(ex)
        if isinstance(ex, KeyError):
            msg = "Incorrect header field(s) in CSV file: {}".format(ex)
        logging.exception(msg)
        return error_json(msg)


@auth_check(roles=["SUP"])
def save_leave_rule():
    try:
        fd = request.get_json(force=True)
        # TODO: validation
        rid = fd.get("id") or 0
        mod = LeaveRule.get_by_id(rid) if rid else LeaveRule()
        merge_json_to_model(mod, fd)
        if not fd.get("valid_till"):
            mod.valid_till = None
        rc = 0
        if rid:
            rc = update_entity(LeaveRule, mod)
        else:
            rc = save_entity(mod)
        if rc == 1:
            return ok_json(model_to_dict(mod))
        else:
            return error_json("Could not save the data. Please try again later!")

    except Exception as ex:
        msg = log_error(ex, "Error when saving leave rule.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def find_leave_rule():
    try:
        fd = request.get_json(force=True)
        pg_no = int(fd.get('pg_no', 1))
        leave_type, sub_role = fd.get('leave_type'), fd.get('sub_role')
        encashable, valid_from = fd.get('encashable'), fd.get('valid_from')
        query = LeaveRule.select()
        query = query.where(LeaveRule.is_deleted != True)
        if sub_role and sub_role != "ANY":
            query = query.where(LeaveRule.sub_role == sub_role)
        if leave_type and leave_type != "ANY":
            query = query.where(LeaveRule.leave_type == leave_type)
        if encashable:
            query = query.where(LeaveRule.encashable == encashable)
        if valid_from:
            query = query.where(LeaveRule.valid_from >= valid_from)

        rules = query.order_by(-LeaveRule.id).paginate(pg_no, PAGE_SIZE)
        serialized = [model_to_dict(x) for x in rules]
        has_next = len(rules) >= PAGE_SIZE
        res = {"ruleList": serialized, "pg_no": pg_no, "pg_size": PAGE_SIZE,
               "has_next": has_next}
        return ok_json(res)

    except Exception as ex:
        msg = log_error(ex, "Error when finding leave rules.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def get_leave_rule(rid):
    try:
        lr = LeaveRule.get_by_id(rid)
        return ok_json(model_to_dict(lr))
    except Exception as ex:
        msg = log_error(ex, "Error when finding leave rules.")
        return error_json(msg)


@auth_check
def get_leave_appl(appl_id):
    try:
        appl = LeaveApplication.get_by_id(appl_id)
        _check_access(appl.user.id, appl.leave_type)
        res = model_to_dict(appl)
        res["status_history"] = _get_audit(appl_id, "leaveapplication")
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when loading leave application.")
        return error_json(msg)


def _get_audit(ent_id, ent_name):
    las = AuditLog.select(AuditLog.old_row_data, AuditLog.dml_type)
    las = las.where(AuditLog.entity_id==ent_id)
    las = las.where(AuditLog.entity_name==ent_name)
    las = las.where(AuditLog.dml_type=="UPDATE")
    lst = [model_to_dict(x) for x in las]
    return lst


@auth_check
def find_leave_appl():
    try:
        fd = request.get_json(force=True)
        pg_no = int(fd.get('pg_no', 1))
        user_id = fd.get('user_id', '')
        leave_type = fd.get('leave_type', '')
        start_dt = fd.get('start_dt') or None
        end_dt = fd.get('end_dt') or None
        area = fd.get('area', '')
        status = fd.get('status', '')
        
        # Acts as role based filters
        if is_user_in_role(["HOD", "MGR"]):
            # Manager and areas chairs see their own areas
            area = session_user()["area"]
        if is_user_in_role(["STA", "FAC", "STA-CON", "FAC-CON"]):
            # A non-manager sees his own data only
            user_id = logged_in_user().id

        qry = LeaveApplication.select(LeaveApplication, User, UserProfile)
        qry = qry.join(User)
        # Join with current profile only
        qry = qry.join(UserProfile, JOIN.LEFT_OUTER, \
                on=( \
                    (UserProfile.user == User.id) & \
                    ( \
                        (UserProfile.valid_from <= DT.now()) | \
                        (UserProfile.valid_till >= DT.now()) \
                    )), attr="curr_profile" \
                )
        if status:
            qry = qry.where(LeaveApplication.status == status)
        if user_id:
            qry = qry.where(LeaveApplication.user.id == user_id)
        if start_dt:
            qry = qry.where(LeaveApplication.start_dt >= start_dt)
        if end_dt:
            qry = qry.where(LeaveApplication.end_dt <= end_dt)
        if leave_type:
            qry = qry.where(LeaveApplication.leave_type == leave_type)
        if area:
            qry = qry.where(UserProfile.area == area)
        
        qry = qry.order_by(-LeaveApplication.id).paginate(pg_no, PAGE_SIZE)
        serialized = []
        for r in qry:
            obj = model_to_dict(r, max_depth=1, recurse=False)
            obj["first_name"] = r.user.first_name
            obj["last_name"] = r.user.last_name
            obj["role"] = r.user.role
            obj["area"] = r.user.curr_profile.area
            obj["doj"] = r.user.curr_profile.doj
            serialized.append(obj)
        has_next = len(qry) >= PAGE_SIZE
        res = {"items": serialized, "pg_no": pg_no, "pg_size": PAGE_SIZE,
               "has_next": has_next}
        return ok_json(res)

    except Exception as ex:
        msg = log_error(ex, "Error when finding leave applications.")
        return error_json(msg)


def _calc_quota_for_rolling(rule, doj):
    to_dt = rule.valid_till or DT.now().date()
    from_dt = max(doj, rule.valid_from)
    return round((to_dt - from_dt).days/365 * rule.yearly_quota, 3)


def _get_current_leave_quota_for_user(user_id):
    u = User.get_by_id(user_id)
    if not u.profiles.exists():
        raise AppException("Please first create a profile for user {}.".format(u.email))
    
    up = u.profiles.where((UserProfile.valid_from <= DT.now()) | \
                        (UserProfile.valid_till >= DT.now()))
    doj = up[0].doj
    lrq = LeaveRule.select() #.where(LeaveRule.valid_from <= doj)
    lrq = lrq.where((LeaveRule.valid_till >= doj) |
                    (LeaveRule.valid_till.is_null()))
    lrq = lrq.where(LeaveRule.sub_role == u.role).order_by(-LeaveRule.valid_from)
    quota = {"CO": 0}
    for rec in lrq:
        if rec.leave_type not in quota:
            quota[rec.leave_type] = 0
        if rec.rolls_over:
            yearly_quota = _calc_quota_for_rolling(rec, doj)
            quota[rec.leave_type] += yearly_quota
            quota[rec.leave_type] = min(quota[rec.leave_type], rec.max_accrual)
        else:
            quota[rec.leave_type] = rec.yearly_quota

    # Comp offs
    wq = u.work_requests
    # Consider expiry of compoff in 15 days of end date
    wq = wq.where(WorkRequest.end_dt <= (DT.today() + timedelta(days=15)))
    wq = wq.where(WorkRequest.status.in_(["APP", "COM"]))
    for wr in wq:
        quota["CO"] += (wr.end_dt - wr.start_dt).days
    return quota


def _get_leaves_availed(user_id):
    # laq = LeaveApplication.select(LeaveApplication.leave_type,
    #         fn.COUNT(LeaveApplication.id).alias("leaves_taken"))
    laq = LeaveApplication.select()
    laq = laq.where(LeaveApplication.user == user_id)
    laq = laq.where(LeaveApplication.status.in_(["APP", "COM"]))
    # laq = laq.group_by(LeaveApplication.leave_type)
    data = {}
    for rec in laq:
        if rec.leave_type not in data:
            data[rec.leave_type] = 0
        days = (rec.end_dt - rec.start_dt).days
        data[rec.leave_type] += days
    return data


@auth_check
def save_leave_appl():
    try:
        fd = request.get_json(force=True)
        aid = fd.get("id", 0)
        appl = LeaveApplication.get_by_id(aid) if aid else LeaveApplication()
        old_status = appl.status 
        merge_json_to_model(appl, fd)
        end_dt = DT.strptime(appl.end_dt, "%Y-%m-%d")
        start_dt = DT.strptime(appl.start_dt, "%Y-%m-%d")
        if start_dt > end_dt:
            return error_json("Start date cannot be after the end date!")
        cu = logged_in_user()
        
        if appl.leave_type == "VL":
            # Check for dates in case of vacation leave
            _check_holiday_dates(start_dt, end_dt, "VAC")
        
        user_id = appl.user.id if aid else cu.id
        availed = _get_leaves_availed(user_id).get(appl.leave_type, 0)
        quota = _get_current_leave_quota_for_user(user_id).get(appl.leave_type, 0)
        days = (end_dt - start_dt).days
        if (availed + days) > quota:
            msg = "Insufficient leaves. Available = {0}. Consumed + Requested = {1} + {2}".format(quota, availed, days)
            return error_json(msg)
        
        rc, rc_expected = 0, 1
        if aid:
            # TODO: Access check
            _check_request_status(old_status, appl.status, appl.start_dt)
            rc = update_entity(LeaveApplication, appl)
        else:
            appl.user = cu.id
            if appl.status not in ["DRA", "SUB"]:
                appl.status = "DRA"
            rc = save_entity(appl)
    
        if rc != rc_expected:
            raise AppException("Could not save the leave application.")

        res = model_to_dict(appl)
        return ok_json(res)

    except Exception as ex:
        msg = log_error(ex, "Error when saving leave application.")
        return error_json(msg)


@auth_check
def get_leave_status(user_id):
    try:
        _check_access(user_id)
        u = User.get_by_id(user_id)
        cpro = get_current_profile(u)
        user = model_to_dict(u, recurse=False)
        user["profile"] = model_to_dict(cpro, recurse=False)
        consumed = _get_leaves_availed(user_id)
        quota = _get_current_leave_quota_for_user(user_id)
        data = []
        for lv_typ, lv_quota in quota.items():
            lv_cons = consumed.get(lv_typ, 0)
            data.append((lv_typ, lv_quota, lv_cons, lv_quota - lv_cons))
        res = {"user": user, "data": data}
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when loading leaves status.")
        return error_json(msg)


@auth_check
def get_credits(typ, for_dd):
    try:
        if typ == "AD":
            res = AdminDutyCredit.select()
        else:
            res = ResearchCredit.select()
        
        if for_dd == "Y":
            ser = [{"id": x.id, "value": x.to_string() } for x in res]
        else:
            ser = [model_to_dict(x) for x in res]

        return ok_json(ser)
    except Exception as ex:
        msg = log_error(ex, "Error when loading credits list.")
        return error_json(msg)


@auth_check(roles=["SUP", "DIR", "DEA"])
def save_admin_duty_credit():
    try:
        fd = request.get_json(force=True)
        aid = fd.get("id", 0)
        adc = AdminDutyCredit.get_by_id(aid) if aid else AdminDutyCredit()
        merge_json_to_model(adc, fd)
        if not fd.get("valid_till"):
            adc.valid_till = None

        if aid:
            rc = update_entity(AdminDutyCredit, adc)
        else:
            rc = save_entity(adc)
        if rc != 1:
            return error_json("Could not save the admin duty credit.")
        else:
            res = model_to_dict(adc)
            return ok_json(res)

    except Exception as ex:
        msg = log_error(ex, "Error when saving admin duty credit.")
        return error_json(msg)


@auth_check
def get_admin_duty_credit(myid):
    try:
        adc = AdminDutyCredit.get_by_id(myid)
        res = model_to_dict(adc)
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when fetching admin duty credit.")
        return error_json(msg)


@auth_check(roles=["SUP", "DIR", "DEA"])
def delete_admin_duty_credit(myid):
    try:
        rc = AdminDutyCredit.delete_by_id(myid)
        if rc == 1:
            return ok_json("Deleted the admin duty credit.")
        else:
            return error_json("Failed to delete the admin duty credit.")
    except Exception as ex:
        msg = log_error(ex, "Error when fetching deleting duty credit.")
        return error_json(msg)


@auth_check(roles=["SUP", "DIR", "DEA"])
def save_research_credit():
    try:
        fd = request.get_json(force=True)
        rcid = fd.get("id", 0)
        mod = ResearchCredit.get_by_id(rcid) if rcid else ResearchCredit()
        merge_json_to_model(mod, fd)
        if not fd.get("valid_till"):
            mod.valid_till = None
        if rcid:
            rc = update_entity(ResearchCredit, mod)
        else:
            rc = save_entity(mod)
        if rc != 1:
            return error_json("Could not save the research credit.")
        else:
            res = model_to_dict(mod)
            return ok_json(res)

    except Exception as ex:
        msg = log_error(ex, "Error when saving research credit.")
        return error_json(msg)


@auth_check
def get_research_credit(myid):
    try:
        adc = ResearchCredit.get_by_id(myid)
        res = model_to_dict(adc)
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when fetching research credit.")
        return error_json(msg)


@auth_check(roles=["SUP", "DIR", "DEA"])
def delete_research_credit(myid):
    try:
        rc = ResearchCredit.delete_by_id(myid)
        if rc == 1:
            return ok_json("Deleted the research credit.")
        else:
            return error_json("Failed to delete the research credit.")
    except Exception as ex:
        msg = log_error(ex, "Error when fetching deleting research credit.")
        return error_json(msg)


@auth_check
def get_activities_for_user(uid):
    try:
        # TODO: Access checks
        u = User.get_by_id(uid)
        aq = u.admin_activities
        rq = u.research_activities
        data = {"adminWork": [], "pubs": []}
        data["userName"] = "{0} {1}".format(u.first_name, u.last_name)
        data["adminWork"] = [model_to_dict(x, recurse=False) for x in aq]
        data["pubs"] = [model_to_dict(x, recurse=False) for x in rq]
        return ok_json(data)
    except Exception as ex:
        msg = log_error(ex, "Error when fetching activities.")
        return error_json(msg)


def _validate_activity_status(st_old, st_new):
    if (not st_old and st_new == "DRA") or (st_new == st_old):
        return
    if is_user_in_role(["SUP", "DIR"]):
        return
    # Status transitions allowed for various roles
    trans_allowed = {"FAC": ["DRA-SUB", "SUB-WIT"],
            "STA": ["DRA-SUB", "SUB-WIT"],
            "MGR": ["SUB-APP", "SUB-REJ", "APP-REJ"],
            "DEA": ["SUB-APP", "SUB-REJ", "APP-REJ"]}
    
    trans_actual = "{0}-{1}".format(st_old, st_new)
    trans = trans_allowed[current_role()]
    if not trans_actual in trans:
        raise AppException("Status change not allowed!")


def _save_activity(atype, fd):
    fd = request.get_json(force=True)
    aid = fd.get("id", 0)
    mod = None
    if "RES" == atype:
        mod = ResearchActivity.get_by_id(aid) if aid else ResearchActivity()
    elif "AD" == atype:
        mod = AdminActivity.get_by_id(aid) if aid else AdminActivity()
    else:
        raise AppException("Unknown activity type: {}".format(atype))
    
    _validate_activity_status(mod.status, fd.get("status"))

    merge_json_to_model(mod, fd)
    if not fd.get("end_dt"):
        mod.end_dt = None

    cu = logged_in_user()
    
    if aid:
        # TODO: Access check
        if "RES" == atype:
            rc = update_entity(ResearchActivity, mod)
        else:
            rc = update_entity(AdminActivity, mod)
    else:
        mod.user = cu.id
        rc = save_entity(mod)
    
    if rc != 1:
        raise AppException("Could not save the user activity.")
    else:
        return model_to_dict(mod)


def _fetch_activity(aid, atype):
    act = None
    if "AD" == atype:
        act = AdminActivity.get_by_id(aid)
    elif "RES" == atype:
        act = ResearchActivity.get_by_id(aid)
    else:
        raise AppException("Unknown activity type: {}".format(atype))
    
    # TODO: Access check
    return act


@auth_check
def save_admin_activity():
    try:
        fd = request.get_json(force=True)
        res = _save_activity("AD", fd)
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when saving admin activity.")
        return error_json(msg)


@auth_check
def save_pub_activity():
    try:
        fd = request.get_json(force=True)
        res = _save_activity("RES", fd)
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when saving research activity.")
        return error_json(msg)


@auth_check(roles=["DIR", "SUP", "MGR", "HOD"])
def find_user_activities(status):
    try:
        rq = ResearchActivity.select().where(ResearchActivity.status == status)
        aq = AdminActivity.select().where(AdminActivity.status == status)
        myarea = None
        if is_user_in_role(["MGR", "HOD"]):
            myarea = session_user()["area"]
        user_ids = set()
        data = []
        for items in (rq, aq):
            for obj in items:
                if obj.user.id in user_ids:
                    continue
                up = obj.user.profiles.where(
                                (UserProfile.valid_from <= DT.now()) | \
                                (UserProfile.valid_till >= DT.now()))
                doj, area = up[0].doj, up[0].area
                if myarea and area != myarea:
                    continue
                res = model_to_dict(obj.user)
                res["area"], res["doj"] = area, doj
                data.append(res)
                user_ids.add(obj.user.id)
        
        return ok_json(data) 

    except Exception as ex:
        msg = log_error(ex, "Error when finding activities.")
        return error_json(msg)


@auth_check
def get_user_activity(aid, atype):
    try:
        act = _fetch_activity(aid, atype)
        res = model_to_dict(act)
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when fetching user activity.")
        return error_json(msg)


@auth_check
def delete_user_activity(aid, atype):
    try:
        act = _fetch_activity(aid, atype)
        rc = act.delete_instance()
        if rc == 1:
            return ok_json("Deleted the user activity.")
        else:
            return error_json("Failed to delete the user activity.")
    except Exception as ex:
        msg = log_error(ex, "Error when deleting activity.")
        return error_json(msg)


def _check_holiday_dates(start_dt, end_dt, hol_type="ALL"):

    """Check whether the dates (inclusive) fall within any holidays.

    Args:
        start_dt (date): Start date for leave
        end_dt (date): End date (inclusive)
        hol_type (str, optional): Type of holiday to check. Defaults to "ALL".
    Raises:
        AppException: When the dates supplied do not fall during a holiday.
    """
    dt_s = DT.strptime(start_dt, "%Y-%m-%d") if isinstance(start_dt, str) else start_dt
    dt_e = DT.strptime(end_dt, "%Y-%m-%d") if isinstance(end_dt, str) else end_dt
    if dt_e < dt_s:
        raise AppException("Start date must be earlier than end date!")
    lq = HolidayInfo.select()
    if hol_type not in ["ALL", "BLK"]:
        lq = lq.where(HolidayInfo.period_type == hol_type)
    lq = lq.where(HolidayInfo.start_dt <= start_dt)
    lq = lq.where(HolidayInfo.end_dt >= end_dt)

    # Weekend check
    is_weekend = dt_s.weekday() in [5, 6] and \
                    dt_e.weekday() in [5, 6] and \
                    (dt_e - dt_s).days <= 2

    if not lq.exists() and not is_weekend:
        raise AppException("Dates {0} and {1} do not fall in holidays or a weekend.".format(start_dt, end_dt))


@auth_check
def save_work_request():
    try:
        fd = request.get_json(force=True)
        wrid = fd.get("id", 0)
        wreq = WorkRequest.get_by_id(wrid) if wrid else WorkRequest()
        old_status = wreq.status
        merge_json_to_model(wreq, fd)
        _check_holiday_dates(wreq.start_dt, wreq.end_dt)
        if wrid:
            # TODO: Access check
            _check_request_status(old_status, wreq.status, wreq.start_dt)
            rc = update_entity(WorkRequest, wreq)
        else:
            wreq.user = logged_in_user().id
            upr = get_current_profile(logged_in_user())
            if not upr.allowed_compoff:
                raise AppException("The user is not entitled for comp-offs.")
            if wreq.status not in ["DRA", "SUB"]:
                wreq.status = "DRA"
            rc = save_entity(wreq)
        if rc != 1:
            return error_json("Could not save the Work Request.")
        else:
            res = model_to_dict(wreq)
            return ok_json(res)

    except Exception as ex:
        msg = log_error(ex, "Error when saving Work Request.")
        return error_json(msg)


@auth_check
def get_work_request(wreq_id):
    try:
        wreq = WorkRequest.get_by_id(wreq_id)
        _check_wr_access(wreq.user.id)
        res = model_to_dict(wreq)
        res["status_history"] = _get_audit(wreq_id, "workrequest")
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when loading work request.")
        return error_json(msg)

@auth_check
def find_work_requests():
    try:
        fd = request.get_json(force=True)
        pg_no = int(fd.get('pg_no', 1))
        user_id = fd.get('user_id', '')
        start_dt = fd.get('start_dt') or None
        end_dt = fd.get('end_dt') or None
        area = fd.get('area', '')
        status = fd.get('status', '')
        
        # For role based filtering
        if is_user_in_role(["HOD", "MGR"]):
            area = session_user()["area"]
        if is_user_in_role(["STA", "FAC", "FAC-CON", "STA-CON"]):
            user_id = logged_in_user().id

        qry = WorkRequest.select(WorkRequest, User, UserProfile)
        qry = qry.join(User)
        # Join with current profile only
        qry = qry.join(UserProfile, JOIN.LEFT_OUTER, \
                on=( \
                    (UserProfile.user == User.id) & \
                    ( \
                        (UserProfile.valid_from <= DT.now()) | \
                        (UserProfile.valid_till >= DT.now()) \
                    )), attr="curr_profile" \
                )
        if area:
            qry = qry.where(UserProfile.area == area)
        if user_id:
            qry = qry.where(WorkRequest.user.id == user_id)
        if start_dt:
            qry = qry.where(WorkRequest.start_dt >= start_dt)
        if end_dt:
            qry = qry.where(WorkRequest.end_dt <= end_dt)
        if status:
            qry = qry.where(WorkRequest.status == status)
        
        qry = qry.order_by(-WorkRequest.id).paginate(pg_no, PAGE_SIZE)
        serialized = []
        for r in qry:
            obj = model_to_dict(r)
            up = model_to_dict(r.user.curr_profile)
            obj["user"]["profile"] = up
            serialized.append(obj)
        has_next = len(qry) >= PAGE_SIZE
        res = {"items": serialized, "pg_no": pg_no, "pg_size": PAGE_SIZE,
               "has_next": has_next}
        return ok_json(res)

    except Exception as ex:
        msg = log_error(ex, "Error when searching Work Requests.")
        return error_json(msg)


@auth_check
def get_form_actions(form_nm, status):
    try:
        qry = FormAction.select(FormAction.action, FormAction.status_after)
        qry = qry.where(FormAction.form == form_nm)
        qry = qry.where(FormAction.status_now.in_([status, "ANY"]))
        qry = qry.where(FormAction.user_role.in_([current_role(), "ANY"])).distinct()
        ser = [{"arg": x.status_after, "label": x.action} for x in qry]
        return ok_json(ser)
    except Exception as ex:
        msg = log_error(ex, "Error when loading form actions for this user.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def all_form_actions():
    try:
        qry = FormAction.select()
        ser = [model_to_dict(x) for x in qry]
        return ok_json(ser)
    except Exception as ex:
        msg = log_error(ex, "Error when loading form actions.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def save_form_action():
    try:
        fd = request.get_json(force=True)
        fa_id = fd.get("id", 0)
        ra = FormAction.get_by_id(fa_id) if fa_id else FormAction()
        merge_json_to_model(ra, fd)
        if fa_id:
            rc = update_entity(FormAction, ra)
        else:
            ra.user = logged_in_user().id
            rc = save_entity(ra)
        if rc != 1:
            return error_json("Could not save the form action.")
        else:
            res = model_to_dict(ra)
            return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when saving form action.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def delete_form_action(fa_id):
    try:
        act = FormAction.get_by_id(fa_id)
        rc = act.delete_instance()
        if rc == 1:
            return ok_json("Deleted the form action.")
        else:
            return error_json("Failed to delete the form action.")
    except Exception as ex:
        msg = log_error(ex, "Error when deleting form action.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def save_holiday():
    try:
        fd = request.get_json(force=True)
        hol_id = fd.get("id", 0)
        hobj = HolidayInfo.get_by_id(hol_id) if hol_id else HolidayInfo()
        merge_json_to_model(hobj, fd)
        if hol_id:
            rc = update_entity(HolidayInfo, hobj)
        else:
            rc = save_entity(hobj)
        if rc != 1:
            return error_json("Could not save the holiday.")
        else:
            res = model_to_dict(hobj)
            return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when saving holiday.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def delete_holiday(hid):
    try:
        act = HolidayInfo.get_by_id(hid)
        rc = act.delete_instance()
        if rc == 1:
            return ok_json("Deleted the holiday.")
        else:
            return error_json("Failed to delete the holiday.")
    except Exception as ex:
        msg = log_error(ex, "Error when deleting holiday.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def load_holidays(year, holType):
    try:
        qry = HolidayInfo.select().where(HolidayInfo.start_dt.year == year)
        if holType != "ALL":
            qry = qry.where(HolidayInfo.period_type == holType)
        res = [model_to_dict(x) for x in qry]
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when loading holidays for year "+str(year))
        return error_json(msg)


@auth_check
def is_blackout(start_dt, end_dt):
    try:
        if start_dt > end_dt:
            raise AppException("End date cannot be earlier than start date!")
        lq = HolidayInfo.select()
        lq = lq.where(HolidayInfo.period_type == "BLK")
        lq = lq.where(
            (HolidayInfo.start_dt.between(start_dt, end_dt)) |
            (HolidayInfo.end_dt.between(start_dt, end_dt)) )
        return ok_json(lq.exists())
    except Exception as ex:
        msg = log_error(ex, "Error when checking for blackout.")
        return error_json(msg)