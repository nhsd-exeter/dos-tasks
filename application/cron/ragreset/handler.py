# import psycopg2
# import psycopg2.extras
from utilities import logger, common, database
from datetime import datetime
import os

task_description = "Reset RAG"


def request(event, context):
    start = datetime.utcnow()
    # message.send_start_message(event, start)
    print("Event: {}".format(event))
    # TODO env from env vars
    env = os.getenv("ENVIRONMENT")
    event_id = event["id"]
    event_time = event["time"]
    logger.log_for_audit(event_id + " " + event_time)
    db_connection = database.connect_to_database(env, event, start)
    reset_rag_status()
    common.cron_cleanup(db_connection)
    return task_description + " execution successful"


def reset_rag_status():
    logger.log_for_audit("Placeholder reset rag status")
