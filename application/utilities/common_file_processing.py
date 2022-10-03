from utilities.logger import log_for_audit
import common
import csv

create_action = "CREATE"
update_action = "UPDATE"
delete_action = "DELETE"
blank_lines = "BLANK"
error_lines = "ERROR"


def check_ids_csv_values(line, env):
    """Returns false if either id1 or id2 are null or empty string"""
    valid_values = True
    try:
        int(line[0])
    except ValueError:
        log_for_audit(env, "action:validation | Problem:Id {} must be a integer".format(line[0]))
        valid_values = False
    if not str(line[0]):
        log_for_audit(env, "action:validation | Problem:Id {} can not be null or empty".format(line[0]))
        valid_values = False
    try:
        int(line[1])
    except ValueError:
        log_for_audit(env, "action:validation | Problem:Id {} must be a integer".format(line[1]))
        valid_values = False
    if not str(line[1]):
        log_for_audit(env, "action:validation | Problem:Id {} can not be null or empty".format(line[1]))
        valid_values = False
    return valid_values


def process_ids_file(csv_file, event, expected_col_count, summary_count_dict):
    """returns dictionary of row data keyed on row number col1=id1, col2=id2, col3=action"""
    lines = {}
    count = 0
    csv_reader = csv.reader(csv_file.split("\n"))
    for line in csv_reader:
        count += 1
        if len(line) == 0:
            common.increment_summary_count(summary_count_dict, "BLANK", event["env"])
            continue
        if common.check_csv_format(line, expected_col_count, event["env"], count) and check_ids_csv_values(
            line, event["env"]
        ):
            lines[str(count)] = {"id1": line[0], "id2": line[1], "action": line[2]}
        else:
            common.increment_summary_count(summary_count_dict, "ERROR", event["env"])
    return lines
