from .. import logger, common


def test_log_for_audit(caplog):
    mock_msg = "Test log for audit function"
    logger.log_for_audit('test', mock_msg)
    assert caplog.text == "INFO     audit:logger.py:15 | task-type:housekeeping | task-name:utilities | env:test | Test log for audit function\n"


def test_log_for_diagnostics(caplog):
    mock_msg = "Test log for diagnostics function"
    env = 'test'
    logger.log_for_diagnostics(env, mock_msg)
    assert caplog.text == "DEBUG    diagnostics:logger.py:19 | task-type:housekeeping | task-name:utilities | env:test | Test log for diagnostics function\n"


def test_log_for_error(caplog):
    mock_msg = "Test log for error function"
    env = 'test'
    logger.log_for_error(env, mock_msg)
    assert caplog.text == "ERROR    audit:logger.py:23 | task-type:housekeeping | task-name:utilities | env:test | Test log for error function\n"

def test_report_summary_count(caplog):
    """Test summary report log output """
    summary_count = {}
    summary_count={"BLANK": 3, "CREATE": 2,"DELETE": 8, "ERROR": 1,"UPDATE": 4}
    common.report_summary_counts(summary_count, 'test')
    assert caplog.text ==  "INFO     audit:logger.py:15 | task-type:housekeeping | task-name:utilities | env:test | updated:4, inserted:2, deleted:8, blank:3, errored:1\n"
