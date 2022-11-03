from utilities import logger, database

#  Note
#  db table is symptomgroupsymptomdiscriminators
#  job name was abbreviated to symptomggroupdiscriminators
# See test-data.sql and test/integration/test-files/int_symptomgroupdiscriminators.csv
# Will test
# That a new record exists with symptomgroup id of 1121 and symptomdiscriminator id of 4033"
# That an existing record symptomgroup id of 1121 and symptomdiscriminator id of 4017 has been deleted

deleted_symptom_group_id = 1121
deleted_symptom_discriminator_id = 4017
created_symptom_group_id = 1121
created_symptom_discriminator_id = 4033


def get_symptom_group_symptom_discriminators_data(env, db_connection):
    """Returns symptomgroupsymptomdiscriminators under test"""
    result_set = {}
    symptom_group_symptom_discriminators_ids = (created_symptom_group_id,created_symptom_discriminator_id,deleted_symptom_group_id,deleted_symptom_discriminator_id)
    try:
        query = create_symptom_group_symptom_discriminators_query()
        result_set = database.execute_resultset_query(env, db_connection, query, symptom_group_symptom_discriminators_ids)
    except Exception as e:
        logger.log_for_error(
            env,
            "Error checking results for {0} => {1}".format("referral roles", str(e)),
        )
    return result_set

def create_symptom_group_symptom_discriminators_query():
    query = ("""select symptomgroupid, symptomdiscriminatorid from pathwaysdos.symptomgroupsymptomdiscriminators
where symptomgroupid = %s and symptomdiscriminatorid = %s
or symptomgroupid = %s and symptomdiscriminatorid = %s"""
    )
    return query

def check_symptom_group_symptom_discriminators_data(env, db_connection):
    """Returns True if all checks pass ; otherwise returns False"""
    delete_pass = True
    create_pass = False

    result_set = get_symptom_group_symptom_discriminators_data(env, db_connection)
    for symptom_group_symptom_discriminator in result_set:
        sg_id = symptom_group_symptom_discriminator["symptomgroupid"]
        sd_id = symptom_group_symptom_discriminator["symptomdiscriminatorid"]
        if sg_id == deleted_symptom_group_id and sd_id == deleted_symptom_discriminator_id :
            delete_pass = False
            logger.log_for_audit(
                env,
                "Record with symptomgroupid {0} and symptomdiscriminatorid {1} not deleted".format(sg_id,sd_id),
            )
        if sg_id == created_symptom_group_id and sd_id == created_symptom_discriminator_id :
            logger.log_for_audit(
                env,
                "Record with symptomgroupid {0} and symptomdiscriminatorid {1} created".format(sg_id,sd_id),
            )
            create_pass = True
    all_pass = delete_pass and create_pass
    return all_pass

