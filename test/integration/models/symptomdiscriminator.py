from utilities import logger, database

# See test-data.sql and test/integration/test-files/int_symptomgdiscriminators.csv
# Will test
# That a new record exists with id of 20000 and description of "Integration Test Create"
# That an existing record with id of 20001 has updated description of "Integration Test Update"
# That an existing record with id of 20002 has been deleted

deleted_record_id = 20002
updated_record_id = 20001
updated_record_description = "Integration Test Update"
created_record_id = 20000
created_record_description = "Integration Test Create"


def get_symptom_discriminator_data(env, db_connection):
    """Returns symptomdiscriminator data under test"""
    result_set = {}
    symptom_discriminator_ids = (created_record_id,updated_record_id,deleted_record_id)
    try:
        query, data = create_symptom_discriminator_query(symptom_discriminator_ids)
        result_set = database.execute_resultset_query(env, db_connection, query, data)
    except Exception as e:
        logger.log_for_error(
            env,
            "Error checking results for {0} => {1}".format("symptomdiscriminators", str(e)),
        )
    return result_set


def create_symptom_discriminator_query(symptom_discriminator_ids):
    query = (
        """select id, description from pathwaysdos.from symptomdiscriminators where id = %s or id = %s or id = %s;"""
    )
    data = symptom_discriminator_ids
    return query, data


# That a new record exists with id of 2000 and description of "Integration Test Create"
# That an existing record with id of 2001 has updated description of "Integration Test Update"
# That an existing record with id of 2002 has been deleted


def check_symptom_discriminator_data(env, db_connection):
    """Returns True if all checks pass ; otherwise returns False"""
    delete_pass = True
    create_pass = False
    update_pass = False
    result_set = get_symptom_discriminator_data(env, db_connection)
    for symptom_discriminator in result_set:
        sd_id = symptom_discriminator["id"]
        if sd_id == deleted_record_id:
            delete_pass = False
            logger.log_for_audit(
                env,
                "Record with id {0} not deleted".format(sd_id),
            )
        if sd_id == created_record_id:
            create_pass = check_symptom_discriminator_record(env, symptom_discriminator, created_record_description)
        if sd_id == updated_record_id:
            update_pass = check_symptom_discriminator_record(env, symptom_discriminator, updated_record_description)
    all_pass = delete_pass and update_pass and create_pass
    return all_pass


def check_symptom_discriminator_record(env, symptom_discriminator, expected_description):
    """Returns true if data persisted is as expected"""
    if symptom_discriminator["description"] == expected_description :
        return True
    else:
        logger.log_for_audit(
                env,
                "Record with id:{0}, description:{1} not correct".format(symptom_discriminator["id"],symptom_discriminator["description"]),
            )
        return False
