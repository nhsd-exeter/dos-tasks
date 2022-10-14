from utilities import logger, database

# See test-data.sql and test/integration/test-files/int_referralroles.csv
# Will test
# That a new record exists with id of 2000 and description of "Integration Test Create"
# That an existing record with id of 2001 has updated description of "Integration Test Update"
# That an existing record with id of 2002 has been deleted

deleted_record_id = 2002
updated_record_id = 2001
updated_record_name = "Integration Test Update"
created_record_id = 2000
created_record_name = "Integration Test Create"
expected_zcode_exists = False


def get_referral_roles_data(env, db_connection):
    """Returns referralroles under test"""
    result_set = {}
    referral_role_ids = (2000,2001,2002)
    try:
        query, data = create_referral_role_query(referral_role_ids)
        result_set = database.execute_resultset_query(env, db_connection, query, data)
    except Exception as e:
        logger.log_for_error(
            env,
            "Error checking results for {0} => {1}".format("referral roles", str(e)),
        )
    return result_set

def create_referral_role_query(referral_role_ids):
    query = (
        """select id, name from pathwaysdos.referralrole where id in """+str(referral_role_ids)+""" order by id asc;"""
    )
    data = str(referral_role_ids)
    return query, data


# That a new record exists with id of 2000 and description of "Integration Test Create"
# That an existing record with id of 2001 has updated description of "Integration Test Update"
# That an existing record with id of 2002 has been deleted


def check_referral_roles_data(env, db_connection):
    """Returns True if all checks pass ; otherwise returns False"""
    delete_pass = True
    create_pass = False
    update_pass = False
    result_set = get_referral_roles_data(env, db_connection)
    for referral_role in result_set:
        rr_id = referral_role["id"]
        if rr_id == deleted_record_id:
            delete_pass = False
            logger.log_for_audit(
                env,
                "Record with id {0} not deleted".format(rr_id),
            )
        if rr_id == created_record_id:
            create_pass = check_referral_role_record(env, referral_role, created_record_name)
        if rr_id == updated_record_id:
            update_pass = check_referral_role_record(env, referral_role, updated_record_name)
    all_pass = delete_pass and update_pass and create_pass
    return all_pass


def check_referral_role_record(env, referral_role, expected_name):
    """Returns true if data persisted is as expected"""
    if referral_role["name"] == expected_name:
        return True
    else:
        logger.log_for_audit(
                env,
                "Record with id:{0}, name:{1} not correct".format(referral_role["id"],referral_role["name"]),
            )
        return False
