"""View functions for managing the API.

__author__ = "Balwinder Sodhi"
__copyright__ = "Copyright 2022"
__license__ = "MIT"
__version__ = "0.1"
__status__ = "Development"
"""

import uuid
from flask import request
from werkzeug.utils import secure_filename
from views_common import *


def _check_access(user_id:int, leave_type:str = None):
    cu = session_user()
    myrole = cu["role"]
    if cu["id"] == user_id or is_user_in_role(["SUP"]):
        return
    uobj = User.get_by_id(user_id)
    # TODO



def _check_request_status(old_status, new_status, start_dt):
    dt = DT.strptime(start_dt, "%Y-%m-%d") if isinstance(start_dt, str) else start_dt
    faq = DocAction.select().where(DocAction.status_after == new_status)
    faq = faq.where(DocAction.status_now.in_([old_status, "ANY"]))
    faq = faq.where(DocAction.user_role.in_(["ANY", current_role()]))
    
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


def _get_audit(ent_id, ent_name):
    las = AuditLog.select(AuditLog.old_row_data, AuditLog.dml_type)
    las = las.where(AuditLog.entity_id==ent_id)
    las = las.where(AuditLog.entity_name==ent_name)
    las = las.where(AuditLog.dml_type=="UPDATE")
    lst = [model_to_dict(x) for x in las]
    return lst


@auth_check
def get_form_actions(form_nm, status):
    try:
        qry = DocAction.select(DocAction.action, DocAction.status_after)
        qry = qry.where(DocAction.doc_type == form_nm)
        qry = qry.where(DocAction.status_now.in_([status, "ANY"]))
        qry = qry.where(DocAction.user_role.in_([current_role(), "ANY"])).distinct()
        ser = [{"arg": x.status_after, "label": x.action} for x in qry]
        return ok_json(ser)
    except Exception as ex:
        msg = log_error(ex, "Error when loading form actions for this user.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def all_form_actions():
    try:
        qry = DocAction.select()
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
        ra = DocAction.get_by_id(fa_id) if fa_id else DocAction()
        merge_json_to_model(ra, fd)
        if fa_id:
            rc = update_entity(DocAction, ra)
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
        act = DocAction.get_by_id(fa_id)
        rc = act.delete_instance()
        if rc == 1:
            return ok_json("Deleted the form action.")
        else:
            return error_json("Failed to delete the form action.")
    except Exception as ex:
        msg = log_error(ex, "Error when deleting form action.")
        return error_json(msg)

