from utilities.logger import log_for_audit, log_for_error  # noqa

def check_csv_format(csv_row,csv_column_count):
    """Checks length of csv data"""
    if len(csv_row) == csv_column_count:
        return True
    else:
        log_for_audit("CSV format invalid - invalid length")
        return False

def valid_action(record_exists, row_data):
    """Returns True if action is valid; otherwise returns False"""
    valid_action = False
    if record_exists and row_data["action"] in ("UPDATE", "DELETE"):
        valid_action = True
    if not record_exists and row_data["action"] in ("CREATE"):
        valid_action = True
    if not valid_action:
        log_for_error("Invalid action {} for the record with ID {}".format(row_data["action"], row_data["id"]))
    return valid_action
