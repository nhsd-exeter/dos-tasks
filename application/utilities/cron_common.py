from utilities.logger import log_for_audit, log_for_error  # noqa


def cron_cleanup(env, db_connection):
    # Close DB connection
    log_for_audit(env, "| Closing DB connection...")
    db_connection.close()
    return "Cleanup Successful"
