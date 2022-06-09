import os
import json
import psycopg2
from utilities import secrets, logger, message

db_host_key = "DB_HOST"
db_user_key = "DB_USER"
db_password_key = "DB_USER_PASSWORD"
secret_store = os.environ.get("SECRET_STORE")
profile = os.environ.get("PROFILE")


class DB:
    def __init__(self) -> None:
        print("Initialising DB Class")
        self.db_host = ""
        self.db_name = ""
        self.db_user = ""
        self.db_password = ""

    def db_set_connection_details(self, env, event, start):
        secret_list = secrets.SECRETS().get_secret_value(secret_store, event, start)
        formatted_secrets = json.loads(secret_list, strict=False)
        connection_details_set = True

        if formatted_secrets is not None:
            if db_host_key in formatted_secrets:
                self.db_host = formatted_secrets[db_host_key]
                logger.log_for_diagnostics("Host: {}".format(self.db_host))
            else:
                connection_details_set = False
                logger.log_for_diagnostics("No DB_HOST secret var set")
            if db_user_key in formatted_secrets:
                self.db_user = formatted_secrets[db_user_key]
                logger.log_for_diagnostics("User: {}".format(self.db_user))
            else:
                connection_details_set = False
                logger.log_for_diagnostics("No DB_USER secret var set")
            if db_password_key in formatted_secrets:
                self.db_password = formatted_secrets[db_password_key]
                logger.log_for_diagnostics("DB_PASSWORD secret set")
            else:
                connection_details_set = False
                logger.log_for_diagnostics("No DB_PASSWORD secret set")
            if profile != "prod" and env != "performance":
                self.db_name = "pathwaysdos_{}".format(env)
            else:
                self.db_name = "pathwaysdos"
            logger.log_for_diagnostics("DB Name: {}".format(self.db_name))
        else:
            connection_details_set = False
            logger.log_for_diagnostics("Secrets not set")
        return connection_details_set

    def db_connect(self, event, start):
        try:
            return psycopg2.connect(
                host=self.db_host, dbname=self.db_name, user=self.db_user, password=self.db_password
            )
        except Exception:
            logger.log_for_error("Connection parameters not set correctly")
            message.send_failure_slack_message(event, start)
            raise psycopg2.InterfaceError()
