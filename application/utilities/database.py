import os
import json
import psycopg2
import psycopg2.extras
from utilities import secrets, logger, common

secret_store = os.environ.get("SECRET_STORE")
profile = os.environ.get("PROFILE")

def derive_db_name(env):
    if env == 'template':
        return 'pipeline_template_latest'
    else:
        return  "pathwaysdos_{}".format(env)

def close_connection(env, db_connection):
    # Close database connection
    if db_connection is not None:
        logger.log_for_audit(env, "action=close DB connection")
        db_connection.close()
    else:
        logger.log_for_error(env, "action=no DB connection to close")


# TODO move inside class later
def connect_to_database(env):
    db = DB()
    logger.log_for_audit(env, "action=establish database connection")
    if not db.db_set_connection_details(env):
        logger.log_for_error(env, "Error DB Parameter(s) not found in secrets store.")
        raise ValueError("DB Parameter(s) not found in secrets store")
    return db.db_connect(env)


# TODO move inside class later
def does_record_exist(db, row_dict, table_name, env):
    """
    Checks to see if record already exists in db table with the id
    """
    record_exists = False
    full_table_name = "pathwaysdos." + table_name
    try:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            select_query = """select * from """ + full_table_name + """ where id=%s"""
            cursor.execute(select_query, (row_dict["id"],))
            if cursor.rowcount != 0:
                record_exists = True
    except (Exception, psycopg2.Error) as e:
        logger.log_for_error(
            env,
            "Select from table {0} by id failed - {1} => {2}".format(full_table_name, row_dict["id"], str(e)),
        )
        raise e
    return record_exists


# TODO move inside class later
def execute_db_query(db_connection, query, data, line, values, summary_count_dict, env):
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(query, data)
        db_connection.commit()
        common.increment_summary_count(summary_count_dict, values["action"], env)
        log = ""
        for x, y in values.items():
            log = log + x + "=" + str(y) + " | "
        logger.log_for_audit(
            env,
            "action=Process row | {} | line number={}".format(log[:-2], line),
        ),
    except Exception as e:
        logger.log_for_error(env, "Line {} in transaction failed. Rolling back".format(line))
        logger.log_for_error(env, "Error: {}".format(e))
        common.increment_summary_count(summary_count_dict, "ERROR", env)
        db_connection.rollback()
    finally:
        cursor.close()


def execute_resultset_query(env, db_connection, query, data):
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(query, data)
        rows = cursor.fetchall()
        db_connection.commit()
        return rows
        # TODO add logging as required
    except Exception as e:
        logger.log_for_error(env, "Transaction failed. Rolling back. Error: {}".format(e))
        db_connection.rollback()
    finally:
        cursor.close()


def execute_query(env, db_connection, query, data):
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(query, data)
        db_connection.commit()
        # TODO add logging as required
    except Exception as e:
        logger.log_for_error(env, "Transaction failed. Rolling back. Error: {}".format(e))
        db_connection.rollback()
    finally:
        cursor.close()


def execute_script(env, db_connection, script):
    cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(open(script, "r").read())
        db_connection.commit()
    except Exception as e:
        logger.log_for_error(env, "Script {} failed. Rolling back. Error: {}".format(script, e))
        db_connection.rollback()
    finally:
        cursor.close()


class DB:
    def __init__(self) -> None:
        self.db_host = ""
        self.db_name = ""
        self.db_user = ""
        self.db_password = ""

    def db_set_connection_details(self, env):
        secret_list = secrets.SECRETS().get_secret_value(secret_store, env)
        formatted_secrets = json.loads(secret_list, strict=False)
        connection_details_set = True
        db_host_key = "DB_HOST"
        db_user_key = "DB_USER"
        db_password_key = "DB_USER_PASSWORD"
        if env == "performance":
            db_host_key = "DB_PERFORMANCE_HOST"
            db_password_key = "DB_PERFORMANCE_PASSWORD"
        if env == "regression":
            db_host_key = "DB_REGRESSION_HOST"

        if formatted_secrets is not None:
            if db_host_key in formatted_secrets:
                self.db_host = formatted_secrets[db_host_key]
            else:
                connection_details_set = False
                logger.log_for_diagnostics(env, "No DB_HOST secret var set")
            if db_user_key in formatted_secrets:
                self.db_user = formatted_secrets[db_user_key]
            else:
                connection_details_set = False
                logger.log_for_diagnostics(env, "No DB_USER secret var set")
            if db_password_key in formatted_secrets:
                self.db_password = formatted_secrets[db_password_key]
            else:
                connection_details_set = False
                logger.log_for_diagnostics(env, "No DB_PASSWORD secret set")
            if profile != "live" and env != "performance":
                self.db_name = derive_db_name(env)
            else:
                self.db_name = "pathwaysdos"
            logger.log_for_diagnostics(
                env,
                "DB name={} |  user={} | host={}".format(self.db_name, self.db_user, self.db_host),
            )
        else:
            connection_details_set = False
            logger.log_for_diagnostics(env, "Secrets not set")
        return connection_details_set

    def db_connect(self, env):
        try:
            return psycopg2.connect(
                host=self.db_host, dbname=self.db_name, user=self.db_user, password=self.db_password
            )
        except Exception as e:
            logger.log_for_error(env, "Connection parameters not set correctly")
            raise psycopg2.InterfaceError(e)
