from utilities import logger, database

#  Note
#  db tables are scenarios and scenariobundles
#  See test-data.sql (clears down all bundles/scenarios0 and test/integration/test-files/36.2.0_stt.zip
#  Will test
#  That there is only one record in scenarionbundlees table

expected_stt_bundle_name = '36.2.0'

expected_disposition_id = 1
expected_disposition_group_id = 18
expected_scenario_id = 893
expected_symptomgroup_id = 1014
expected_symptom_discriminator_id = 4499
expected_age_id = 1
expected_gender_id = 2


def get_stt_scenario_data(env, db_connection):
    """Returns expected data on all stt scenario bundles and scenarios within bundles"""
    result_set = {}
    try:
        query = create_stt_scenarios_query()
        result_set = database.execute_resultset_query(env, db_connection, query, ())
    except Exception as e:
        logger.log_for_error(
            env,
            "Error checking results for {0} => {1}".format("referral roles", str(e)),
        )
    return result_set

def create_stt_scenarios_query():
    query = ("""select sb.name, s.scenarioid, s.symptomgroupid, s.dispositionid, s.dispositiongroupid, s.symptomdiscriminatorid,
    s.ageid, s.genderid
    from scenariobundles sb
    join scenarios s
    on s.scenariobundleid = sb.id"""
    )
    return query

def check_scenario_data_item(env, scenario, column_name, expected_value):
    ok = True
    if scenario[column_name] != expected_value:
        ok = False
        logger.log_for_audit(
            env,
            "Column name {0} set to {1} and not expected value of {2}".format(column_name,scenario[column_name],expected_value),
        )
    return ok


def check_stt_scenario_data(env, db_connection):
    """Returns True if single record in resultset and all checks pass ; otherwise returns False"""
    flags = []
    result_set = get_stt_scenario_data(env, db_connection)
    for scenario in result_set:
        flags.append(check_scenario_data_item(env, scenario, "name", expected_stt_bundle_name))
        flags.append(check_scenario_data_item(env, scenario, "scenarioid", expected_scenario_id))
        flags.append(check_scenario_data_item(env, scenario, "dispositionid", expected_disposition_id))
        flags.append(check_scenario_data_item(env, scenario, "dispositiongroupid", expected_disposition_group_id))
        flags.append(check_scenario_data_item(env, scenario, "symptomgroupid", expected_symptomgroup_id))
        flags.append(check_scenario_data_item(env, scenario, "symptomdiscriminatorid", expected_symptom_discriminator_id))
        flags.append(check_scenario_data_item(env, scenario, "ageid", expected_age_id))
        flags.append(check_scenario_data_item(env, scenario, "genderid", expected_gender_id))
    if len(flags)==0:
        flags.append(False)
    return all(flags)

