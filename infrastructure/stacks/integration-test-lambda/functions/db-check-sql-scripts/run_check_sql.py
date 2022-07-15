import boto3
from botocore.exceptions import ClientError
from run_update_check import run_check
import psycopg2
import os
import json

USERNAME = os.environ.get("USERNAME")
PORT = os.environ.get("PORT")
REGION = os.environ.get("REGION")
SOURCE_ENDPOINT = os.environ.get("SOURCE_ENDPOINT")
TARGET_ENDPOINT = os.environ.get("TARGET_ENDPOINT")
FALLBACK_ENDPOINT = os.environ.get("FALLBACK_ENDPOINT")



MINIMUM_SEQUENCE_INCREMENT = int(os.environ.get("MINIMUM_SEQUENCE_INCREMENT"))

valid_sql_filenames = {"check_databases.sql", "check_db_size.sql",
"check_roles.sql","check_tablespace_sizes.sql","check_tablespaces.sql",
"pk_check.sql","check_fks.sql","check_extensions.sql","check_sequences.sql","update_check",
"check_table_sizes.sql"}

def get_secret():

    secret_name = SECRET_NAME
    region_name = REGION

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if "SecretString" in get_secret_value_response:
            return get_secret_value_response["SecretString"]
        else:
            return base64.b64decode(get_secret_value_response["SecretBinary"])

#  AB - source is a ; target is B
#  BC - source is b ; target is C
#  It is imperative that the SOURCE_ENDPOINT is NEVER used as the target endpoint
def derive_source_endpoint(instance_pair):
    if instance_pair.upper() == "AB":
        return SOURCE_ENDPOINT
    elif instance_pair.upper() == "BC":
        return TARGET_ENDPOINT
    else :
        return ""

def derive_target_endpoint(instance_pair):
    if instance_pair.upper() == "AB":
        return TARGET_ENDPOINT
    elif instance_pair.upper() == "BC":
        return FALLBACK_ENDPOINT
    else :
        return ""

# Method to connect to database
def connect(endpoint,database_name):
    try:
        secret_dict = json.loads(get_secret())
        conn = psycopg2.connect(
            host=endpoint,
            port=PORT,
            user=USERNAME,
            database=database_name,
            password=secret_dict[SECRET_KEY],
        )
        return conn
    except Exception as e:
        print("Database connection failed due to {}".format(e))
        raise e


# Method to get cursor from db
def getCursor(conn):
    try:
        cur = conn.cursor()
        return cur
    except Exception as e:
        print("unable to retrieve cursor due to {}".format(e))
        conn.close()
        raise e

# Prints out results from the source and target cursors
def print_results(source_cursor, target_cursor, instance_pair):

    print("Output from source " + derive_source_endpoint(instance_pair))
    for source_record in source_cursor:
        print("---")
        print(source_record)

    print("Output from target " + derive_target_endpoint(instance_pair))
    for target_record in target_cursor:
        print("---")
        print(target_record)

# Compares a source list against a target list
def comparator(compare_from, compare_to):
    same = True

    for source_item in compare_from:
        # See if FK exists in the target list
        if source_item not in compare_to:
            print("FK not in target: " + str(source_item))
            same = False

    return same

# Compares the fk results returned by the given cursors that are passed
# through
def compare_fks(source_cursor, target_cursor):
    source_list = list()
    target_list = list()

    for source_record in source_cursor:
        source_list.append(source_record)

    for target_record in target_cursor:
        target_list.append(target_record)

    if(len(source_list)==0):
        print("There are no FKs present in the source DB")
        return False

    if(len(target_list)==0):
        print("There are no FKs present in the target DB")
        return False

    print ("Comparing Source FKs with Target FKs...")
    same = comparator(source_list, target_list)

    if same:
        print ("No differences between source and target FKs")

    print ("Comparing Target FKs with Source FKs...")
    same_reverse = comparator(target_list, source_list)

    return (same and same_reverse)

# Compares the sequences results returned by the given cursors that are passed
# through
def compare_sequences(source_cursor, target_cursor):

    valid = False
    source_seq_dict = {}
    for source_record in source_cursor:
        source_seq_dict.update({source_record[0]: source_record[1]})

    target_seq_dict = {}
    for target_record in target_cursor:
        target_seq_dict.update({target_record[0]: target_record[1]})

    if len(source_seq_dict)==0:
        print("There are no sequences present in the source DB")
        return False

    if len(target_seq_dict)==0:
        print("There are no sequences present in the target DB")
        return False

    print ("Comparing Source sequences with Target sequences...")
    valid = sequence_comparator(source_seq_dict,target_seq_dict)

    return valid

# Returns false if any sequence in source is missing in target or
# sequence value in target is not higher than sequence value in source
def sequence_comparator(compare_from_dict, compare_to_dict):
    valid = True
    for key in compare_from_dict:
        # See if sequence exists in the target list
        print ("Checking sequence " + str(key))
        if key not in compare_to_dict:
            print("Sequence " + str(key) + " not in target: ")
            valid = False
        else :
            source_sequence_value = compare_from_dict.get(key)
            target_sequence_value = compare_to_dict.get(key)
            if target_sequence_value - source_sequence_value < MINIMUM_SEQUENCE_INCREMENT:
                print("Value of Sequence " + str(key) + " is " + str(source_sequence_value) + " in source and " + str(target_sequence_value) + " in target" )
                valid = False
    return valid

# Compares the table sizes returned by the given cursors that are passed
# through
def compare_table_sizes(source_cursor, target_cursor, source_conn, target_conn):

    valid = False
    source_tab_dict = {}
    for source_record in source_cursor:
        source_tab_dict.update({source_record[0]: source_record[1]})

    target_tab_dict = {}
    for target_record in target_cursor:
        target_tab_dict.update({target_record[0]: target_record[1]})

    if len(source_tab_dict)==0:
        print("There are no tables present in the source DB")
        return False

    if len(target_tab_dict)==0:
        print("There are no tables present in the target DB")
        return False

    print ("Reporting Source table sizes that are different in target...")
    valid = table_size_comparator(source_tab_dict,target_tab_dict, source_conn, target_conn)

    return valid

# Returns false if any table size in source is different from
# table size in target. Prints notification for such tables
# Table size measured by comparing sizes of each table column.
def table_size_comparator(compare_from_dict, compare_to_dict, source_conn, target_conn):

    valid = True
    source_cur = getCursor(source_conn)
    target_cur = getCursor(target_conn)
    for key in compare_from_dict:
        # See if table exists in the target list
        if key not in compare_to_dict:
            print("Table " + str(key) + " not in target: ")
            valid = False
        else :
            source_table_col_size_query = compare_from_dict.get(key)
            target_table_col_size_query = compare_to_dict.get(key)

            source_cur.execute(source_table_col_size_query)
            source_tab_col_size_str = source_cur.fetchone()

            target_cur.execute(target_table_col_size_query)
            target_tab_col_size_str = target_cur.fetchone()

            if source_tab_col_size_str != target_tab_col_size_str :
                print("Size of Table " + str(key) + " columns is " + str(source_tab_col_size_str) + " in source and " + str(target_tab_col_size_str) + " in target" )

                valid = False

    source_cur.close()
    target_cur.close()

    return valid

# Method to obtain current values (+100) of all sequences in source db
def run_sql(sql_file, database_name, instance_pair):
    # get connection and cursor for source
    print("Opening source connection")
    source_conn = connect(derive_source_endpoint(instance_pair),database_name)
    print("Source connection opened")
    source_cur = getCursor(source_conn)
    # get connection and cursor for target
    print("Opening target connection")
    target_conn = connect(derive_target_endpoint(instance_pair),database_name)
    print("Target Connection opened")
    target_cur = getCursor(target_conn)

    ret_val = True

    try:
        source_cur.execute(open(sql_file, "r").read())
        target_cur.execute(open(sql_file, "r").read())

        if sql_file == "check_fks.sql" :
            ret_val = compare_fks(source_cur, target_cur)
        elif sql_file == "check_sequences.sql" :
            ret_val = compare_sequences(source_cur, target_cur)
        elif sql_file == "check_table_sizes.sql" :
            ret_val = compare_table_sizes(source_cur, target_cur, source_conn, target_conn)
        else:
            print_results(source_cur, target_cur, instance_pair)

    except Exception as e:
        print("SQL script failed due to {}".format(e))
        return False
    finally:
        source_cur.close()
        source_conn.close()
        target_cur.close()
        target_conn.close()
        print("PostgreSQL connection is closed")
    return ret_val

# Checks that the sql-file name given in the run event is valid (one that
# we are expecting)
def is_valid_file(file_name):
    valid_file = False
    for x in valid_sql_filenames:
        if (x.lower() ==  file_name.lower()):
            valid_file = True
            break
    if valid_file == False:
        print("Invalid file name. Please check name of sql script")
    return valid_file

# This is the entry point for the Lambda function
# expects name of sql script to be run passed as argument of the event
def lambda_handler(event, context):

    print("Start of handler")
    sql_file = event['sql-file']
    database_name = event['database_name']
    instance_pair = event['instance_pair']
    print("File:" + sql_file)
    print("Database: " + database_name)
    print("Migration pair to compare: " + instance_pair)
    # Connect to source and run query
    if is_valid_file(sql_file):
        if sql_file == 'update_check':
            outcome = run_check(database_name,instance_pair);
        else:
            outcome = run_sql(sql_file,database_name,instance_pair)
    else:
        outcome = False

    status_code = 200 if outcome else 500

    return {"statusCode": status_code, "body": str(outcome) + " result"}
