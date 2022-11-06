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


def _check_doc_action(doc_item):
    if is_user_in_role("SUP"):
        return # Superuser is allowed all actions
    
    cu = session_user()
    my_role, my_ou = cu["role"], cu["org_unit"]
    daq = doc_item.doc_type.doc_actions
    daq = daq.where(DocAction.status_now.in_([doc_item.status, "ANY"]))
    daq = daq.where(DocAction.user_role.in_(["ANY", my_role]))
    daq = daq.where(DocAction.allowed_ou.contains(my_ou))
    
    if not daq.exists():
        raise AppException("Change not allowed.")


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
        qry = DocAction.select().join(DocType)
        qry = qry.where(DocType.name == form_nm)
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
        
        ra = DocAction.get_by_id(ra.id)
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


@auth_check(roles=["SUP"])
def delete_doc_field(my_id):
    try:
        act = DocField.get_by_id(my_id)
        rc = act.delete_instance()
        if rc == 1:
            return ok_json("Deleted the doc field.")
        else:
            return error_json("Failed to delete the doc field.")
    except Exception as ex:
        msg = log_error(ex, "Error when deleting doc field.")
        return error_json(msg)

@auth_check
def get_doc_type_fields(doc_type):
    try:
        dtq = DocType.select().where(DocType.name == doc_type)
        if not dtq.exists():
            return error_json("Doc type not found!")
        
        df = [model_to_dict(x, recurse=False) for x in dtq[0].doc_fields]
        return ok_json(df)
    except Exception as ex:
        msg = log_error(ex, "Error loading doc fields.")
        return error_json(msg)

@auth_check(roles=["SUP"])
def save_doc_field():
    try:
        fd = request.get_json(force=True)
        fa_id = fd.get("id", 0)
        ra = DocField.get_by_id(fa_id) if fa_id else DocField()
        merge_json_to_model(ra, fd)
        if fa_id:
            rc = update_entity(DocField, ra)
        else:
            rc = save_entity(ra)
        if rc != 1:
            return error_json("Could not save the doc field.")
        
        ra = DocField.get_by_id(ra.id)
        res = model_to_dict(ra, recurse=False)
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when saving doc field.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def save_doc_type():
    try:
        fd = request.get_json(force=True)
        fa_id = fd.get("id", 0)
        ra = DocType.get_by_id(fa_id) if fa_id else DocType()
        merge_json_to_model(ra, fd)
        if fa_id:
            rc = update_entity(DocType, ra)
        else:
            rc = save_entity(ra)
        if rc != 1:
            return error_json("Could not save the doc type.")
        else:
            res = model_to_dict(ra)
            return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when saving doc type.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def find_doc_type():
    try:
        fd = request.get_json(force=True)
        name = fd.get("name")
        pg_no = int(fd.get('pg_no', 1))
        dtq = DocType.select()
        dtq = dtq.where(DocType.is_deleted != True)
        if name:
            dtq = dtq.where(DocType.name.contains(name))
        data = dtq.order_by(-DocType.id).paginate(pg_no, PAGE_SIZE)
        serialized = [model_to_dict(r) for r in data]
        has_next = len(data) >= PAGE_SIZE
        res = {"items": serialized, "pg_no": pg_no, "pg_size": PAGE_SIZE,
               "has_next": has_next}
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when searching doc type.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def get_doc_type(my_id):
    try:
        dt = DocType.get_by_id(my_id)
        df = [model_to_dict(x, recurse=False) for x in dt.doc_fields]
        res = model_to_dict(dt, recurse=False)
        res["doc_fields"] = df
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when fetching doc type.")
        return error_json(msg)


@auth_check(roles=["SUP"])
def get_all_doc_types():
    try:
        dt = DocType.select()
        data = [{"id": x.id, "value": x.name} for x in dt]
        return ok_json(data)
    except Exception as ex:
        msg = log_error(ex, "Error when fetching doc types.")
        return error_json(msg)


def _fetch_doc_item(my_id):
    di = DocItem.get_by_id(my_id)
    df = [f.doc_file for f in di.doc_files]
    dn = [model_to_dict(n, recurse=False) for n in di.doc_notes]
    data = model_to_dict(di, recurse=False)
    data["doc_files"] = df
    data["doc_notes"] = dn
    return data


@auth_check
def get_doc_item(my_id):
    try:
        di = _fetch_doc_item(my_id)
        return ok_json(di)
    except Exception as ex:
        msg = log_error(ex, "Error when fetching doc item.")
        return error_json(msg)


@auth_check
def save_doc_item():
    try:
        fd = {}
        for (k, v) in request.form.items():
            if v not in ["null", "undefined", ""]:
                if v == "true":
                    fd[k] = True
                elif v == "false":
                    fd[k] = False
                else:
                    fd[k] = v
        
        editing = "id" in fd
        dtn = fd["doc_type_name"]
        dtq = DocType.select().where(DocType.name==dtn)
        if not dtq.exists():
            raise AppException("Doc type {} not found!".format(dtn))
        fd["doc_type"] = dtq[0].id
        dfl = request.files.getlist("dataFiles")
        files_info = []
        for file in dfl:
            file_path, fname = _save_uploaded_file(file, "DOCITEM")
            files_info.append((file_path, fname))
        
        with db.transaction() as txn:
            di = DocItem.get_by_id(int(fd["id"])) if editing else DocItem()
            merge_json_to_model(di, fd)
            rc = 0
            if editing:
                rc = update_entity(DocItem, di)
            else:
                rc = save_entity(di)
            if rc != 1:
                raise AppException("Failed to save doc item. Please retry later.")

            din = DocItemNote(doc_item=di.id, note=fd["action_note"])
            rc += save_entity(din)

            for fin in files_info:
                dif = DocItemFile(doc_item=di.id, doc_file=fin[1])
                rc += save_entity(dif)
            
            if rc != len(files_info) + 2:
                raise AppException("Failed to save some items. Please retry later.")

        res = _fetch_doc_item(di.id)
        return ok_json(res)
    except Exception as ex:
        msg = log_error(ex, "Error when saving doc item.")
        return error_json(msg)