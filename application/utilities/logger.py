from logging import getLogger, INFO, DEBUG
import os

msg_prefix = os.environ.get("TASK")
audit_logger = getLogger("audit")
diagnostic_logger = getLogger("diagnostics")
audit_logger.setLevel(INFO)
diagnostic_logger.setLevel(DEBUG)


def log_for_audit(msg_log):
    audit_logger.info("{} | {}".format(msg_prefix, msg_log))


def log_for_diagnostics(msg_log):
    diagnostic_logger.debug("{} | {}".format(msg_prefix, msg_log))


def log_for_error(msg_log):
    audit_logger.error("{} | {}".format(msg_prefix, msg_log))
