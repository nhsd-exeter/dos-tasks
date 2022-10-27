from utilities import logger, database

# See test-data.sql and test/integration/test-files/int_servicetypes.csv
# Will test
# That a new record exists with id of 2000 and description of "Integration Test Create"
# That an existing record with id of 2001 has updated description of "Integration Test Update"
# That an existing record with id of 2002 has been deleted

deleted_record_id = 2002
updated_record_id = 2001
updated_record_name = "Integration Test Update"
created_record_id = 2000
created_record_name = "Integration Test Create"
expected_national_ranking = 8
expected_search_capacity_status = True
expected_capacity_model = "n/a"
expected_capacity_reset = "interval"

def get_service_types_data(env, db_connection):
    """Returns servicetypes under test"""
    result_set = {}
    service_type_ids = "(2000,2001,2002)"
    try:
        query, data = create_service_type_query(service_type_ids)
        result_set = database.execute_resultset_query(env, db_connection, query, data)
    except Exception as e:
        logger.log_for_error(
            env,
            "Error checking results for {0} => {1}".format("servicetypes", str(e)),
        )
    return result_set


def create_service_type_query(service_type_ids):
    query = (
        """select id, name, nationalranking, searchcapacitystatus, capacitymodel, capacityreset from servicetypes where id in (2000,2001,2002);"""
    )
    data = service_type_ids
    return query, data


# That a new record exists with id of 2000 and description of "Integration Test Create"
# That an existing record with id of 2001 has updated description of "Integration Test Update"
# That an existing record with id of 2002 has been deleted
def check_service_types_data(env, db_connection):
    """Returns True if all checks pass ; otherwise returns False"""
    delete_pass = True
    create_pass = False
    update_pass = False
    result_set = get_service_types_data(env, db_connection)
    for service_type in result_set:
        st_id = service_type["id"]
        if st_id == deleted_record_id:
            delete_pass = False
            logger.log_for_audit(
                env,
                "Record with id {0} not deleted".format(st_id),
            )
        if st_id == created_record_id:
            create_pass = check_service_type_record(env, service_type, created_record_name, expected_national_ranking)
            update_pass = check_service_type_record(env, service_type, updated_record_name, expected_national_ranking)
    all_pass = delete_pass and update_pass and create_pass
    return all_pass

def check_service_type_record(env, service_type, expected_name, expected_national_ranking):
    """Returns true if data persisted is as expected"""
    if service_type["name"] == expected_name and service_type["nationalranking"] == expected_national_ranking and service_type["capacityreset"] ==  expected_capacity_reset and service_type["capacitymodel"] == expected_capacity_model and service_type["searchcapacitystatus"] == expected_search_capacity_status:
        return True
    else:
        logger.log_for_audit(
                env,
                "Record with id:{0}, name:{1}, nationalranking:{2} not correct".format(service_type["id"],service_type["name"],service_type["nationalranking"]),
            )
        return False
