import logging

prefix_delimiter = "|"
auditlogger = logging.getLogger("audit")
diaglogger = logging.getLogger("diagnostics")
auditlogger.setLevel(logging.INFO)
diaglogger.setLevel(logging.DEBUG)


def log_for_audit(msg_prefix, log_text):
    auditlogger.info(msg_prefix + prefix_delimiter + log_text)


def log_for_diagnostics(msg_prefix, log_text):
    diaglogger.debug(msg_prefix + prefix_delimiter + log_text)


def log_for_error(msg_prefix, log_text):
    auditlogger.error(msg_prefix + prefix_delimiter + log_text)
