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
        processed = process_zipfile(env, db_connection, bundle, filename)
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


# input_zip = zipfile.ZipFile(io.BytesIO(bundle_zip))
#     for name in input_zip.namelist():
#         print("=========== name ============")
#         scenario_file = input_zip.read(name).decode("utf-8")
#         print(scenario_file)


def process_zipfile(env, db_connection, bundle, filename):
    processed = True
    try:
        bundle_zip = zipfile.ZipFile(io.BytesIO(bundle))
        for name in bundle_zip.namelist():
            logger.log_for_audit(env, "action:processing scenario {}".format(name))
            scenario_file = bundle_zip.read(name).decode("utf-8")
            try:
                # template_scenario = process_scenario_file(name, io.StringIO(scenario_file.decode("utf-8")))
                template_scenario = process_scenario_file(name, scenario_file)
                insert_template_scenario(db_connection, template_scenario)
            except Exception as e:
                processed = False
                logger.log_for_error("stt", "Problem processing scenario file {0}: {1}".format(name, e))
                raise e
    except Exception as e:
        processed = False
        logger.log_for_error("stt", "Problem processing {0} -> {1}".format(filename, e))
    return processed


# def process_zipfile(db_connection, filename):
#     processed = True
#     if zipfile.is_zipfile(filename):
#         with zipfile.ZipFile(filename, mode="r") as archive:
#             for name in archive.namelist():
#                 scenario_file = archive.read(name)
#                 try:
#                     template_scenario = process_scenario_file(name, io.StringIO(scenario_file.decode("utf-8")))
#                     insert_template_scenario(db_connection, template_scenario)
#                 except Exception as e:
#                     processed = False
#                     logger.log_for_error("stt", "Problem processing scenario file {0}: {1}".format(name, e))
#     else:
#         processed = False
#         logger.log_for_error("stt", "Release bundle {0} is not a zip file".format(filename))
#     return processed


def insert_template_scenario(db_connection, template_scenario):
    query, data = get_insert_query(template_scenario)
    database.execute_query(db_connection, query, data)


def get_insert_query(template_scenario):
    query = """insert into pathwaysdos.searchscenarios (releaseid, scenarioid, symptomgroup_uid, triagedispositionuid,
    triage_disposition_description, final_disposition_group_cmsid, final_disposition_code,
    report_texts, symptom_discriminator_uid, symptom_discriminator_desc_text, scenariofilename,
    scenariofile, created_on)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now()
    )"""
    data = (
        template_scenario.pathways_release_id,
        template_scenario.file_name,
        template_scenario.symptom_group,
        template_scenario.triage_disposition_uid,
        template_scenario.triage_disposition_description,
        template_scenario.final_disposition_group_cmsid,
        template_scenario.final_disposition_code,
        template_scenario.report_texts,
        template_scenario.symptom_discriminator_uid,
        template_scenario.symptom_discriminator_desc_text,
        template_scenario.file_name,
        template_scenario.file_name,
    )
    return query, data


def process_scenario_file(file_name, scenario_file):
    try:
        scenario_dict = map_xml_to_json(scenario_file)
        # scenario_dictroot = get_root(scenario_file)
        pathways_release_id = get_pathways_release_id(scenario_dict)
        symptom_group = get_symptom_group(scenario_dict)
        triage_disposition_uid = get_triage_disposition_uid(scenario_dict)
        triage_disposition_description = get_triage_disposition_description(scenario_dict)
        final_disposition_group_cmsid = get_final_disposition_group_cmsid(scenario_dict)
        final_disposition_code = get_final_disposition_code(scenario_dict)
        report_texts, symptom_discriminator_uid, symptom_discriminator_desc_text = get_triage_line_data(scenario_dict)
        template_scenario = scenario.Scenario(
            pathways_release_id,
            file_name,
            symptom_group,
            triage_disposition_uid,
            triage_disposition_description,
            final_disposition_group_cmsid,
            final_disposition_code,
            report_texts,
            symptom_discriminator_uid,
            symptom_discriminator_desc_text,
        )
    except ET.ParseError as e:
        print(file_name)
        logger.log_for_error("stt", "Invalid xml {}".format(e))
        raise e

    return template_scenario


def map_xml_to_json(file_as_string):
    return xmltodict.parse(file_as_string)


# def get_root(file_as_string):
#     root_element = ET.fromstring(file_as_string)
#     return root_element

# xmldict alternatives
def get_pathways_release_id(scenario_dict) -> str:
    # pathways_release_id = root.find("./pathwayscase:PathwaysCase/pathwayscase:PathwaysReleaseID", ns)
    pathways_release_id = scenario_dict["NHSPathways"]["PathwaysCase"]["PathwaysReleaseID"]
    release_id = pathways_release_id.split("_")
    return release_id[0]


def get_symptom_group(scenario_dict):
    symptom_group_element = scenario_dict["NHSPathways"]["PathwaysCase"]["SymptomGroup"]
    return symptom_group_element


def get_triage_disposition_uid(scenario_dict):
    disposition_uid = scenario_dict["NHSPathways"]["PathwaysCase"]["TriageDisposition"]["DispositionCode"]
    return disposition_uid


def get_triage_disposition_description(scenario_dict):
    disposition_description = scenario_dict["NHSPathways"]["PathwaysCase"]["TriageDisposition"][
        "DispositionDescription"
    ]
    return disposition_description


def get_final_disposition_group_cmsid(scenario_dict):
    final_disposition_group = scenario_dict["NHSPathways"]["PathwaysCase"]["FinalDispositionCMSID"][
        "FinalDispositionCMSID"
    ]
    return final_disposition_group


def get_final_disposition_code(scenario_dict):
    final_disposition_code = scenario_dict["NHSPathways"]["PathwaysCase"]["FinalDisposition"]["DispositionCode"]
    return final_disposition_code


def get_triage_line_data(scenario_dict):
    report_texts = []
    symptom_discriminator_uid = ""
    symptom_discriminator_desc = ""
    triage_lines = get_triage_lines(scenario_dict)
    for triage_line in triage_lines:
        report_texts = add_report_text(triage_line, report_texts)
        care_advice_sd = triage_line["CareAdvice"]["SymptomDiscriminator"]
        if care_advice_sd != "0":
            symptom_discriminator_uid = care_advice_sd
            symptom_discriminator_desc = triage_line["AnswerText"]
    return report_texts, symptom_discriminator_uid, symptom_discriminator_desc.replace('"', "")


def get_triage_lines(scenario_dict):
    return scenario_dict["NHSPathways"]["PathwaysCase"]["TriageLineDetails"]["TriageLine"]


def add_report_text(triage_line, report_text_list):
    report_text = None
    if triage_line["IncludeInReport"] == "True":
        report_text = triage_line["ReportText"]
    if report_text is not None:
        report_text_list.append(report_text)
    return report_text_list


# def identify_report_elements_to_include(triage_line):
#     return triage_line.find("pathwayscase:IncludeInReport[.='True']", ns)


# def get_report_text(triage_line):
#     report_text = None
#     report_text_element = triage_line.find("pathwayscase:ReportText[.!='']", ns)
#     if report_text_element is not None:
#         report_text = report_text_element.text
#         # TODO may not be needed
#         report_text = report_text.replace('"', "")
#     return report_text


# original

# TODO need to handle exceptions eg non numeric bundles like dental
# def get_pathways_release_id(root) -> str:
#     pathways_release_id = root.find("./pathwayscase:PathwaysCase/pathwayscase:PathwaysReleaseID", ns)
#     release_id = pathways_release_id.text.split("_")
#     return release_id[0]


# def get_symptom_group(root):
#     symptom_group_element = root.find("./pathwayscase:PathwaysCase/pathwayscase:SymptomGroup[1]", ns)
#     return symptom_group_element.text


# def get_triage_disposition_uid(root):
#     disposition_uid = root.find(
#         "./pathwayscase:PathwaysCase/pathwayscase:TriageDisposition/pathwayscase:DispositionCode[1]", ns
#     )
#     return disposition_uid.text


# def get_triage_disposition_description(root):
#     disposition_description = root.find(
#         "./pathwayscase:PathwaysCase/pathwayscase:TriageDisposition/pathwayscase:DispositionDescription[1]", ns
#     )
#     return disposition_description.text


# def get_final_disposition_group_cmsid(root):
#     final_disposition_group = root.find(
#         "./pathwayscase:PathwaysCase/pathwayscase:FinalDispositionCMSID/pathwayscase:FinalDispositionCMSID[1]", ns
#     )
#     return final_disposition_group.text


# def get_final_disposition_code(root):
#     final_disposition_code = root.find(
#         "./pathwayscase:PathwaysCase/pathwayscase:FinalDisposition/pathwayscase:DispositionCode[1]", ns
#     )
#     return final_disposition_code.text


# def get_triage_line_data(root):
#     report_texts = []
#     symptom_discriminator_uid = ""
#     symptom_discriminator_desc_text = ""
#     triage_lines = get_triage_lines(root)
#     for triage_line in triage_lines:
#         report_texts = add_report_text(triage_line, report_texts)
#         care_advice_sd = triage_line.find("pathwayscase:CareAdvice/pathwayscase:SymptomDiscriminator[.!='0']", ns)
#         if care_advice_sd is not None:
#             symptom_discriminator_uid = care_advice_sd.text
#             symptom_discriminator_desc = triage_line.find("pathwayscase:AnswerText", ns)
#             symptom_discriminator_desc_text = symptom_discriminator_desc.text
#     return report_texts, symptom_discriminator_uid, symptom_discriminator_desc_text.replace('"', "")


# def get_triage_lines(root):
#     return root.findall("./pathwayscase:PathwaysCase/pathwayscase:TriageLineDetails/pathwayscase:TriageLine", ns)


# def add_report_text(triage_line, report_text_list):
#     report_text = None
#     if identify_report_elements_to_include(triage_line) is not None:
#         report_text = get_report_text(triage_line)
#     if report_text is not None:
#         report_text_list.append(report_text)
#     return report_text_list


# def identify_report_elements_to_include(triage_line):
#     return triage_line.find("pathwayscase:IncludeInReport[.='True']", ns)


# def get_report_text(triage_line):
#     report_text = None
#     report_text_element = triage_line.find("pathwayscase:ReportText[.!='']", ns)
#     if report_text_element is not None:
#         report_text = report_text_element.text
#         # TODO may not be needed
#         report_text = report_text.replace('"', "")
#     return report_text
