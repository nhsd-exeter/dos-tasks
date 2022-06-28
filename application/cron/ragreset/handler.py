# import psycopg2
# import psycopg2.extras
from application.utilities.logger import log_for_audit, log_for_error
from utilities import logger, common, database
from datetime import datetime
import os

task_description = "Reset RAG"
reset_interval_in_seconds = 14400
ignore_org_types = "1,2"
interval_type = "interval"
new_status = 1
modified_by = "ROBOT"
modified_by_id = 9
notes = ""

def request(event, context):
    start = datetime.utcnow()
    # message.send_start_message(event, start)
    print("Event: {}".format(event))
    # TODO env from env vars
    env = os.getenv("ENVIRONMENT")
    event_id = event["id"]
    event_time = event["time"]
    logger.log_for_audit("Event id: {0}, event time: {1} , environment: {2}".format(event_id, event_time, env))
    # temporarily not needed except for messaging
    payload = {"filename": "NA", "env": env, "bucket": "NA"}
    db_connection = database.connect_to_database(env, payload, start)
    reset_rag_status(db_connection)
    common.cron_cleanup(db_connection)
    return task_description + " execution successful"


def reset_rag_status(db_connection):
    logger.log_for_audit("Start ragreset process")
    update_query, data  = generate_update_query()
    updated_services = database.execute_cron_query(db_connection, update_query, data)
    log_updated_services(updated_services)


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
                and s.typeid not in ((%s))
                )
        returning
        *
    """
    data = (notes, modified_by, modified_by_id, new_status, new_status, interval_type, ignore_org_types)
    return query, data


def log_updated_services(updated_services):
    for service in updated_services:
        try:
            log_for_audit(service["serviceid"])
        except KeyError as e:
            log_for_error("Data returned from db does not include serviceid column ")
            raise e

def generate_service_query(service_id):
    query = """select uid, name, typeid, parentid
            from services
            where id = %s
    """
    data = (service_id,)
    return query, data

def generate_parent_uid_query(service_id):
    query = """select
            ser.id as parentid,
            ser.uid as parentuid
            from services as ser
            where ser.id = (select parentid from services where id = %s)';
    """
    data = (service_id,)
    return query, data


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
    data = (service_id,service_id)
    return query, data
