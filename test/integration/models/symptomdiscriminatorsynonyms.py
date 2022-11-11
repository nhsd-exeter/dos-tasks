from utilities import logger, database

# See test-data.sql and test/integration/test-files/int_symptomgdiscriminatorsynonyms.csv
# Will test
# That a new record exists with symptomdiscriminatorid of 11116 and name of "Integration test create"
# That an existing record with symptomdiscriminatorid of 11009 and name of "Integration test delete" is deleted

deleted_record_sdid = 11009
deleted_record_name= "Integration test delete"
created_record_sdid = 11116
created_record_name= "Integration test create"


def get_symptom_discriminator_synonyms_data(env, db_connection):
    """Returns symptomgdiscriminatorsynonyms under test"""
    result_set = {}
    symptom_discriminator_synonyms_values = (deleted_record_sdid, deleted_record_name, created_record_sdid, created_record_name)
    try:
        query, data = create_symptom_discriminator_synonyms_query(symptom_discriminator_synonyms_values)
        result_set = database.execute_resultset_query(env, db_connection, query, data)
    except Exception as e:
        logger.log_for_error(
            env,
            "Error checking results for {0} => {1}".format("symptom discriminator synonyms", str(e)),
        )

    return result_set

def create_symptom_discriminator_synonyms_query(symptom_discriminator_synonyms_values):
    query = ("""select symptomdiscriminatorid, name from pathwaysdos.symptomdiscriminatorsynonyms
where symptomdiscriminatorid = %s and name = %s
or symptomdiscriminatorid = %s and name = %s"""
    )
    data = symptom_discriminator_synonyms_values
    return query, data

def check_symptom_discriminator_synonyms_data(env, db_connection):
    """Returns True if all checks pass ; otherwise returns False"""
    delete_pass = True
    create_pass = False

    result_set = get_symptom_discriminator_synonyms_data(env, db_connection)
    for symptom_discriminator_synonyms in result_set:
        sds_sdid = symptom_discriminator_synonyms["symptomdiscriminatorid"]
        sds_name = symptom_discriminator_synonyms["name"]
        if sds_sdid == deleted_record_sdid and sds_name == deleted_record_name :
            delete_pass = False
            logger.log_for_audit(
                env,
                "Record with symptomdiscriminatorid {0} and name {1} not deleted".format(sds_sdid, sds_name),
            )
        if sds_sdid == created_record_sdid and sds_name == created_record_name :
            logger.log_for_audit(
                env,
                "Record with symptomdiscriminatorid {0} and name {1} created".format(sds_sdid, sds_name),
            )
            create_pass = True
    all_pass = delete_pass and create_pass
    return all_pass
