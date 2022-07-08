from logging import getLogger, INFO, DEBUG
import os

housekeeping_prefix = "housekeeping"
msg_prefix = os.environ.get("TASK")
audit_logger = getLogger("audit")
diagnostic_logger = getLogger("diagnostics")
audit_logger.setLevel(INFO)
diagnostic_logger.setLevel(DEBUG)

log_structure = "| task-type:{} | task-name:{} | env:{} | {}"


def log_for_audit(env, msg_log):
    audit_logger.info(log_structure.format(housekeeping_prefix, msg_prefix, env, msg_log))


def log_for_diagnostics(env, msg_log):
    diagnostic_logger.debug(log_structure.format(housekeeping_prefix, msg_prefix, env, msg_log))


def log_for_error(env, msg_log):
    audit_logger.error(log_structure.format(housekeeping_prefix, msg_prefix, env, msg_log))
