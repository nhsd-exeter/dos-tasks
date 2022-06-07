from .. import logging


def test_log_for_audit(caplog):
    mock_msg = "Test log for audit function"
    logging.log_for_audit(mock_msg)
    assert caplog.text == "INFO     audit:logging.py:12 utilities | Test log for audit function\n"


def test_log_for_diagnostics(caplog):
    mock_msg = "Test log for diagnostics function"
    logging.log_for_diagnostics(mock_msg)
    assert caplog.text == "DEBUG    diagnostics:logging.py:16 utilities | Test log for diagnostics function\n"


def test_log_for_error(caplog):
    mock_msg = "Test log for error function"
    logging.log_for_error(mock_msg)
    assert caplog.text == "ERROR    audit:logging.py:20 utilities | Test log for error function\n"
