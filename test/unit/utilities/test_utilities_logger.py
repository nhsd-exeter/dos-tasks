from .. import logger


def test_log_for_audit(caplog):
    mock_msg = "Test log for audit function"
    logger.log_for_audit(mock_msg)
    assert caplog.text == "INFO     audit:logger.py:13 housekeeping | utilities | Test log for audit function\n"


def test_log_for_diagnostics(caplog):
    mock_msg = "Test log for diagnostics function"
    logger.log_for_diagnostics(mock_msg)
    assert caplog.text == "DEBUG    diagnostics:logger.py:17 housekeeping | utilities | Test log for diagnostics function\n"


def test_log_for_error(caplog):
    mock_msg = "Test log for error function"
    logger.log_for_error(mock_msg)
    assert caplog.text == "ERROR    audit:logger.py:21 housekeeping | utilities | Test log for error function\n"
