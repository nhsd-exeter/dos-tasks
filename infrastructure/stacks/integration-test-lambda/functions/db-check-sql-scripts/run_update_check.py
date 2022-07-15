import datetime
import time
import boto3
from botocore.exceptions import ClientError
import psycopg2
import os
import json

USERNAME = os.environ.get("USERNAME")
PORT = os.environ.get("PORT")
REGION = os.environ.get("REGION")
SOURCE_ENDPOINT = os.environ.get("SOURCE_ENDPOINT")
TARGET_ENDPOINT = os.environ.get("TARGET_ENDPOINT")
FALLBACK_ENDPOINT = os.environ.get("FALLBACK_ENDPOINT")

REPLICATION_MAX_NO_POLLS = int(os.environ.get("REPLICATION_MAX_NO_POLLS"))
REPLICATION_POLLING_INTERVAL = int(os.environ.get("REPLICATION_POLLING_INTERVAL"))



TARGET_ROW_ID = '999999'

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

# Compares detail text from cursor with the expected detail text
def compare_detail_text(cursor, expected_detail_text):

    for x in range(REPLICATION_MAX_NO_POLLS-1):
        cursor_list = list()
        print("Poll: " + str(x))

        cursor.execute("select detail from pathwaysdos.news where id=" + TARGET_ROW_ID + ";")

        for cursor_record in cursor:
            cursor_list.append(cursor_record[0])

        if(len(cursor_list)==0):
            print("There is no news record present for id " + TARGET_ROW_ID + "!")
            return False

        if (str(cursor_list[0])==expected_detail_text):
            return True

        time.sleep(REPLICATION_POLLING_INTERVAL)

    return (False)

# Confirms that the specified target row is present in either the B or C databases.
def confirm_row_present(cursor, present):

    for x in range(REPLICATION_MAX_NO_POLLS-1):
        cursor_list = list()
        print("Poll: " + str(x))

        cursor.execute("select id from pathwaysdos.news where id=" + TARGET_ROW_ID + ";")

        for cursor_record in cursor:
            cursor_list.append(cursor_record[0])

        if(len(cursor_list)==present):
            return True

        time.sleep(REPLICATION_POLLING_INTERVAL)

    return (False)

# Issues an update command to insert a row from the source database and checks this is
# replicated
def check_update(source_cur, source_conn, rep_target_1_cur, rep_target_2_cur='NO'):
    current_date = str(datetime.datetime.today())
    detail_text = "test content for update " + current_date

    source_cur.execute("update pathwaysdos.news set detail = '" + detail_text + "' where id=" + TARGET_ROW_ID + ";")
    source_conn.commit()
    source_update_timestamp = datetime.datetime.today()
    print ("Source updated timestamp: " + str(source_update_timestamp))

    target_ok = compare_detail_text(rep_target_1_cur, detail_text)
    if not target_ok:
        print("Target replication 1 does not have the expected updated applied.")
        return False
    else:
        target_1_update_timestamp = datetime.datetime.today()
        print ("Target replication 1 updated timestamp: " + str(target_1_update_timestamp))
        timediff = target_1_update_timestamp - source_update_timestamp
        print("Time to replicate update to replication target 1: " + str(timediff))

    if rep_target_2_cur!='NO':
        fallback_ok = compare_detail_text(rep_target_2_cur, detail_text)
        if not fallback_ok:
            print("Target replication 2 does not have the expected updated applied.")
            return False
        else:
            target_2_update_timestamp = datetime.datetime.today()
            print ("Target replication 2 updated timestamp: " + str(target_2_update_timestamp))
            timediff = target_2_update_timestamp - source_update_timestamp
            print("Time to replicate update to replication target 2: " + str(timediff))

    return True

# Issues an insert command to insert a row from the source database and checks this is
# replicated
def check_insert(source_cur, source_conn, rep_target_1_cur, rep_target_2_cur='NO'):
    current_date = str(datetime.datetime.today())
    detail_text = "test content for insert " + current_date

    source_cur.execute("insert into pathwaysdos.news (id, uid, title, detail, creatorname, createtimestamp) values (" + TARGET_ROW_ID + "," + TARGET_ROW_ID + ",'test insert','" + detail_text + "','dms',DEFAULT);")
    source_conn.commit()
    source_insert_timestamp = datetime.datetime.today()
    print ("Source inserted timestamp: " + str(source_insert_timestamp))

    target_ok = confirm_row_present(rep_target_1_cur, present=True)
    if not target_ok:
        print("Target replication 1 does not have the expected insert applied.")
        return False
    else:
        target_1_insert_timestamp = datetime.datetime.today()
        print ("Target replication 1 inserted timestamp: " + str(target_1_insert_timestamp))
        timediff = target_1_insert_timestamp - source_insert_timestamp
        print("Time to replicate insert to replication target 1: " + str(timediff))

    if rep_target_2_cur!='NO':
        fallback_ok = confirm_row_present(rep_target_2_cur, present=True)
        if not fallback_ok:
            print("Target replication 2 does not have the expected insert applied.")
            return False
        else:
            target_2_insert_timestamp = datetime.datetime.today()
            print ("Target replication 2 inserted timestamp: " + str(target_2_insert_timestamp))
            timediff = target_2_insert_timestamp - source_insert_timestamp
            print("Time to replicate insert to replication target 2: " + str(timediff))

    return True

# Issues a delete command to delete a row from the source database and checks this is
# replicated
def check_delete(source_cur, source_conn, rep_target_1_cur, rep_target_2_cur='NO'):

    source_cur.execute("delete from pathwaysdos.news where id=" + TARGET_ROW_ID + ";")
    source_conn.commit()
    source_delete_timestamp = datetime.datetime.today()
    print ("Source deleted timestamp: " + str(source_delete_timestamp))

    target_ok = confirm_row_present(rep_target_1_cur, present=False)
    if not target_ok:
        print("Target replication 1 still has target record present.")
        return False
    else:
        target_1_delete_timestamp = datetime.datetime.today()
        print ("Target replication 1 deleted timestamp: " + str(target_1_delete_timestamp))
        timediff = target_1_delete_timestamp - source_delete_timestamp
        print("Time to replicate delete to replication target 1: " + str(timediff))

    if rep_target_2_cur!='NO':
        fallback_ok = confirm_row_present(rep_target_2_cur, present=False)
        if not fallback_ok:
            print("Target replication 2 still has target record present.")
            return False
        else:
            target_2_delete_timestamp = datetime.datetime.today()
            print ("Target replication 2 deleted timestamp: " + str(target_2_delete_timestamp))
            timediff = target_2_delete_timestamp - source_delete_timestamp
            print("Time to replicate delete to replication target 2: " + str(timediff))

    return True

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
def get_cursor(conn):
    try:
        cur = conn.cursor()
        return cur
    except Exception as e:
        print("unable to retrieve cursor due to {}".format(e))
        conn.close()
        raise e

# Runs insert, update, and delete commands against the source database and check
# that the commands are replicated to B and C in a timely manner
def run_check(database_name, instance_pair):
    # get connection and cursor for source
    print("Opening connections")
    source_conn = connect(SOURCE_ENDPOINT,database_name)
    source_cur = get_cursor(source_conn)
    # get connection and cursor for target
    target_conn = connect(TARGET_ENDPOINT,database_name)
    target_cur = get_cursor(target_conn)
    # get connection and cursor for fallback
    fallback_conn = connect(FALLBACK_ENDPOINT,database_name)
    fallback_cur = get_cursor(fallback_conn)

    ret_val = True

    try:

        if instance_pair=='ABC':
            ret_val = check_insert(source_cur, source_conn, target_cur, fallback_cur)
            if (ret_val):
                ret_val = check_update(source_cur, source_conn, target_cur, fallback_cur)
            if (ret_val):
                ret_val = check_delete(source_cur, source_conn, target_cur, fallback_cur)
        elif instance_pair=='AB':
            ret_val = check_insert(source_cur, source_conn, target_cur)
            if (ret_val):
                ret_val = check_update(source_cur, source_conn, target_cur)
            if (ret_val):
                ret_val = check_delete(source_cur, source_conn, target_cur)
        elif instance_pair=='AC':
            ret_val = check_insert(source_cur, source_conn, fallback_cur)
            if (ret_val):
                ret_val = check_update(source_cur, source_conn, fallback_cur)
            if (ret_val):
                ret_val = check_delete(source_cur, source_conn, fallback_cur)
        elif instance_pair=='BC':
            ret_val = check_insert(target_cur, target_conn, fallback_cur)
            if (ret_val):
                ret_val = check_update(target_cur, target_conn, fallback_cur)
            if (ret_val):
                ret_val = check_delete(target_cur, target_conn, fallback_cur)
        else:
            print("Invalid instance pair.")
            ret_val = False

    except Exception as e:
        print("SQL script failed due to {}".format(e))
        ret_val = False
    finally:
        # Clean up
        source_cur.execute("delete from pathwaysdos.news where id=" + TARGET_ROW_ID + ";")
        source_conn.commit()
        target_cur.execute("delete from pathwaysdos.news where id=" + TARGET_ROW_ID + ";")
        target_conn.commit()
        fallback_cur.execute("delete from pathwaysdos.news where id=" + TARGET_ROW_ID + ";")
        fallback_conn.commit()
        # Close off connections
        source_cur.close()
        source_conn.close()
        target_cur.close()
        target_conn.close()
        fallback_cur.close()
        fallback_conn.close()
        print("PostgreSQL connections closed")
    return ret_val
