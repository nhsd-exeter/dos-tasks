import xml.etree.ElementTree as ET
import zipfile
import io
import xmltodict

#  works but not from docker
# from . import scenario
from utilities import logger, message, common, database, scenario
from datetime import datetime


ns = {"pathwayscase": "http://www.nhspathways.org/webservices/pathways/pathwaysCase"}

task_description = "Import STT scenarios"


def request(event, context):
    start = datetime.utcnow()
    message.send_start_message(event, start)
    filename = event["filename"]
    bucket = event["bucket"]
    env = event["env"]
    db_connection = None
    logger.log_for_audit(event["env"], "action:task started")
    try:
        db_connection = database.connect_to_database(env)
        # TODO will be a compressed file - testing on .zip -  rar?
        bundle = common.retrieve_compressed_file_from_bucket(bucket, filename, event, start)
        logger.log_for_audit(env, "action:bundle {} downloaded".format(filename))
        bundle_id = add_bundle(db_connection, filename)
        logger.log_for_audit(env, "action:bundle {} inserted".format(bundle_id))
        processed = process_zipfile(env, db_connection, bundle, filename, bundle_id)
        if processed is True:
            message.send_success_slack_message(event, start, None)
        else:
            message.send_failure_slack_message(event, start)
        # TODO will need to unpack
    except Exception as e:
        logger.log_for_error(env, "Problem {}".format(e))
        message.send_failure_slack_message(event, start)
    finally:
        database.close_connection(event, db_connection)
        common.archive_file(bucket, filename, event, start)
    return task_description + " execution completed"


def process_zipfile(env, db_connection, bundle, filename, bundle_id):
    processed = True
    try:
        bundle_zip = zipfile.ZipFile(io.BytesIO(bundle))
        for name in bundle_zip.namelist():
            logger.log_for_audit(env, "action:processing scenario {}".format(name))
            scenario_file = bundle_zip.read(name).decode("utf-8")
            try:
                template_scenario = process_scenario_file(name, scenario_file, bundle_id)
                insert_template_scenario(db_connection, template_scenario)
            except Exception as e:
                processed = False
                logger.log_for_error("stt", "Problem processing scenario file {0}: {1}".format(name, e))
                raise e
    except Exception as e:
        processed = False
        logger.log_for_error("stt", "Problem processing {0} -> {1}".format(filename, e))
    return processed


def insert_template_scenario(db_connection, template_scenario):
    query, data = get_scenario_insert_query(template_scenario)
    database.execute_query(db_connection, query, data)


def get_scenario_insert_query(template_scenario):
    query = """insert into scenarios(bundleid, scenarioid, symptomgroupid, dispositionid,
dispositiongroupid, symptomdiscriminatorid, ageid, genderid, triagereport, createdtime
)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,now()
    )"""
    data = (
        template_scenario.bundle_id,
        template_scenario.scenario_id,
        template_scenario.symptom_group_id,
        template_scenario.disposition_id,
        template_scenario.disposition_group_id,
        template_scenario.symptom_discriminator_id,
        template_scenario.age_id,
        template_scenario.gender_id,
        template_scenario.triage_report,
    )
    return query, data


def process_scenario_file(file_name, scenario_file, bundle_id):
    try:
        scenario_dict = map_xml_to_json(scenario_file)
        scenario_id = get_scenario_id(file_name)
        age_id = get_age_id(scenario_dict)
        gender_id = get_gender_id(scenario_dict)
        symptom_group_id = get_symptom_group_id(scenario_dict)
        disposition_id = get_disposition_code(scenario_dict)
        disposition_group_id = get_disposition_group_uid(scenario_dict)
        triage_report, symptom_discriminator_id = get_triage_line_data(scenario_dict)

        template_scenario = scenario.Scenario(
            bundle_id,
            scenario_id,
            symptom_group_id,
            disposition_id,
            disposition_group_id,
            triage_report,
            symptom_discriminator_id,
            age_id,
            gender_id,
        )
    except ET.ParseError as e:
        print(file_name)
        logger.log_for_error("stt", "Invalid xml {}".format(e))
        raise e

    return template_scenario


def map_xml_to_json(file_as_string):
    return xmltodict.parse(file_as_string)


def add_bundle(db_connection, zip_file_name):
    bundle_name = get_bundle_name(zip_file_name)
    query, data = get_bundle_insert_query(bundle_name)
    result_set = database.execute_query(db_connection, query, data)
    return result_set[0]["id"]


def get_bundle_insert_query(bundle_id):
    query = """insert into pathwaysdos.scenariobundles (name,createdtime) values (%s,now()) returning id"""
    data = (bundle_id,)
    return query, data


def get_bundle_name(zip_file_name):
    """Extract name of bundle from provided zip file assuming convention - R33.2.0_STT_Bundle_stt.zip"""
    bundle_parts = zip_file_name.split("_")
    bundle_id = bundle_parts[0]
    start_at_position = 1
    if bundle_id[0] != "R":
        start_at_position = 0
    return bundle_id[start_at_position:]


def get_scenario_id(scenario_file_name):
    """Extract id for scenario from file name allowing for naming conventions used"""
    scenario_name = scenario_file_name.split(".xml")
    delimiter = "Scenario_"
    if delimiter not in scenario_name[0]:
        delimiter = "Scenario "
    scenario_identifier = scenario_name[0].split(delimiter)
    try:
        return int(scenario_identifier[1])
    except ValueError:
        logger.log_for_error("stt", "Problem converting {} to id".format(scenario_identifier[1]))
        raise ValueError("Can't convert {} to int for storing as scenario id".format(scenario_identifier[1]))


def get_age_id(scenario_dict):
    age_id = scenario_dict["NHSPathways"]["PathwaysCase"]["Patient"]["Age"]["AgeID"]
    return age_id


def get_gender_id(scenario_dict):
    gender_id = scenario_dict["NHSPathways"]["PathwaysCase"]["Patient"]["Gender"]["GenderID"]
    return gender_id


def get_symptom_group_id(scenario_dict):
    symptom_group_id = scenario_dict["NHSPathways"]["PathwaysCase"]["SymptomGroup"]
    return symptom_group_id


def get_disposition_code(scenario_dict):
    disposition_uid = scenario_dict["NHSPathways"]["PathwaysCase"]["TriageDisposition"]["DispositionCode"]
    return disposition_uid.upper()


def get_disposition_group_uid(scenario_dict):
    final_disposition_group_uid = scenario_dict["NHSPathways"]["PathwaysCase"]["FinalDispositionCMSID"][
        "FinalDispositionCMSID"
    ]
    return final_disposition_group_uid


def get_triage_line_data(scenario_dict):
    report_texts = []
    symptom_discriminator_id = ""
    triage_lines = get_triage_lines(scenario_dict)
    for triage_line in triage_lines:
        report_texts = add_report_text(triage_line, report_texts)
        care_advice_sd = triage_line["CareAdvice"]["SymptomDiscriminator"]
        if care_advice_sd != "0":
            symptom_discriminator_id = care_advice_sd
    return report_texts, symptom_discriminator_id


def get_triage_lines(scenario_dict):
    return scenario_dict["NHSPathways"]["PathwaysCase"]["TriageLineDetails"]["TriageLine"]


def add_report_text(triage_line, report_text_list):
    report_text = None
    if triage_line["IncludeInReport"] == "True":
        report_text = triage_line["ReportText"]
    if report_text is not None:
        report_text_list.append(report_text)
    return report_text_list
