# import psycopg2
# import psycopg2.extras
from utilities import logger, database, cron_common
from datetime import datetime
import os

task_description = "Reset RAG"
reset_interval_in_seconds = 14400
ignore_org_types = [1, 2]
interval_type = "interval"
new_status = 1
modified_by = "ROBOT"
modified_by_id = 9
notes = ""


def request(event, context):
    print("Event: {}".format(event))
    env = os.getenv("DB_NAME")
    event_id = event["id"]
    event_time = event["time"]
    logger.log_for_audit(env, "operation=start")
    logger.log_for_audit(env, "Event id={0}, event time={1} , environment={2}".format(event_id, event_time, env))
    db_connection = database.connect_to_database(env)
    reset_rag_status(env, db_connection)
    cron_common.cron_cleanup(env, db_connection)
    logger.log_for_audit(env, "operation=end")
    return task_description + " execution successful"


def reset_rag_status(env, db_connection):

    try:
        update_query, data = generate_update_query()
        updated_services = database.execute_resultset_query(env, db_connection, update_query, data)
        log_updated_services(env, db_connection, updated_services)
    except KeyError as e:
        logger.log_for_error(env, "Exception raised running rag reset job {}".format(e))
        raise e


def generate_update_query():
    query = """
        update pathwaysdos.servicecapacities
        set
            notes = (%s),
            modifiedby = (%s),
            modifiedbyid = (%s),
            modifieddate = now(),
            capacitystatusid = (%s),
            resetdatetime = null
        where id in (
            select sercap.id from pathwaysdos.servicecapacities sercap
            join pathwaysdos.services s
            on s.id = sercap.serviceid
            join pathwaysdos.servicetypes st
            on s.typeid = st.id
            where
                sercap.capacitystatusid <> (%s)
                and st.capacityreset = (%s)
                and now() >= sercap.resetdatetime
                and s.typeid not in (%s,%s)
                )
        returning
        *
    """
    data = (
        notes,
        modified_by,
        modified_by_id,
        new_status,
        new_status,
        interval_type,
        ignore_org_types[0],
        ignore_org_types[1],
    )
    return query, data


def get_log_data(env, db_connection, service_id):
    service_data = get_service_data(env, db_connection, service_id)
    parent_data = get_parent_uid(env, db_connection, service_id)
    region_data = get_region_name(env, db_connection, service_id)
    log_info = {}
    log_info["operation"] = "update"
    log_info["capacity_status"] = "GREEN"
    log_info["modified_by"] = modified_by
    log_info["org_id"] = service_data[0]["uid"]
    log_info["org_name"] = service_data[0]["name"]
    log_info["org_type_id"] = service_data[0]["typeid"]
    log_info["parent_org_id"] = parent_data[0]["parentuid"]
    log_info["region"] = region_data[0]["name"]
    return log_info


def get_log_entry(log_info):
    log_text = ""
    for key, value in log_info.items():
        kv_pair = key + ":" + str(value)
        log_text = log_text + "| " + kv_pair + " "
    log_text = log_text + "|"
    return log_text[2:]


def log_updated_services(env, db_connection, updated_services):
    for service in updated_services:
        try:
            service_id = service["serviceid"]
            log_info = get_log_data(env, db_connection, service_id)
            log_text = get_log_entry(log_info)
            logger.log_for_audit(env, log_text)
        except KeyError as e:
            logger.log_for_error(env, "Data returned from db does not include serviceid column ")
            raise e
    format_data = "%b %d %Y %H:%M:%S"
    end_at = datetime.utcnow()
    logger.log_for_audit(
        env,
        "operation=AutoUpdateCapacityStatus | records updated={0} | updated at={1}".format(
            str(len(updated_services)), end_at.strftime(format_data)
        ),
    )


def get_service_data(env, db_connection, service_id):
    query, data = generate_service_query(service_id)
    result_set = database.execute_resultset_query(env, db_connection, query, data)
    return result_set


def generate_service_query(service_id):
    query = """select uid, name, typeid, parentid
            from services
            where id = %s
    """
    data = (service_id,)
    return query, data


def get_parent_uid(env, db_connection, service_id):
    query, data = generate_parent_uid_query(service_id)
    result_set = database.execute_resultset_query(env, db_connection, query, data)
    return result_set


def generate_parent_uid_query(service_id):
    query = """select
            ser.id as parentid,
            ser.uid as parentuid
            from services as ser
            where ser.id = (select parentid from services where id = %s);
    """
    data = (service_id,)
    return query, data


def get_region_name(env, db_connection, service_id):
    query, data = generate_region_name_query(service_id)
    result_set = database.execute_resultset_query(env, db_connection, query, data)
    return result_set


def generate_region_name_query(service_id):
    query = """select
            s.uid,
            s.name,
            (with recursive tree AS(
            select s.id,s.uid,s.parentid,s.name, 1 AS lvl FROM services s where s.id = %s
            union all
            select s.id,s.uid,s.parentid,s.name, lvl+1 AS lvl
            from services s
            inner join tree t ON s.id = t.parentid)
            select name from tree order by lvl desc limit 1) AS dosregion
        from services s
        where s.id = %s
    """
    data = (service_id, service_id)
    return query, data
