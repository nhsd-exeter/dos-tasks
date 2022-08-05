import xml.etree.ElementTree as ET
import zipfile
import io
# from scenario import Scenario
from . import scenario
from utilities import logger, message, common, database
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
        bundle_zip = common.retrieve_file_from_bucket(bucket, filename, event, start)
        process_zipfile(bundle_zip)
        # TODO will need to unpack
    except Exception as e:
        logger.log_for_error(env, "Problem {}".format(e))
        message.send_failure_slack_message(event, start)
    finally:
        database.close_connection(event, db_connection)
        common.archive_file(bucket, filename, event, start)
    return task_description + " execution completed"


def process_zipfile(filename):
    if zipfile.is_zipfile(filename):
        with zipfile.ZipFile(filename, mode="r") as archive:
            for name in archive.namelist():
                scenario_file = archive.read(name)
                process_scenario_file(name,io.StringIO(scenario_file.decode('utf-8')))
    else:
        # TODO
        print("not a zip")


def get_scenario_id_from_file_name(file_name):
    """scenario id can be separated by space or underscore eg Scenario_230.xml or Scenario 330.xml
    sometimes both formats in same release/bundle"""
    elements = file_name.split(".")
    if file_name.count("_") > 0:
        name_elements = elements[0].split("_")
    else:
        name_elements = elements[0].split(" ")
    return name_elements[1].replace('"', "")

def process_scenario_file(file_name, scenario_file):

    tree = get_tree(scenario_file)
    pathways_release_id = get_pathways_release_id(tree)
    symptom_group = get_symptom_group(tree)
    triage_disposition_uid = get_triage_disposition_uid(tree)
    triage_disposition_description = get_triage_disposition_description(tree)
    final_disposition_group_cmsid = get_final_disposition_group_cmsid(tree)
    final_disposition_code = get_final_disposition_code(tree)
    report_texts, symptom_discriminator_uid, symptom_discriminator_desc_text = get_triage_line_data(tree)
    scenar = scenario.Scenario(pathways_release_id, file_name,symptom_group, triage_disposition_uid, triage_disposition_description, final_disposition_group_cmsid, final_disposition_code, report_texts, symptom_discriminator_uid, symptom_discriminator_desc_text)
    return scenar

def get_tree(file):
    tree = ET.parse(file)
    return tree


def get_root(tree):
    return tree.getroot()

# TODO need to handle exceptions eg non numeric bundles like dental
def get_pathways_release_id(tree)-> str:
    pathways_release_id = tree.find("./pathwayscase:PathwaysCase/pathwayscase:PathwaysReleaseID", ns)
    release_id = pathways_release_id.text.split("_")
    return release_id[0]

def get_symptom_group(tree):
    symptom_group_element = tree.find("./pathwayscase:PathwaysCase/pathwayscase:SymptomGroup[1]", ns)
    return symptom_group_element.text


def get_triage_disposition_uid(tree):
    disposition_uid = tree.find(
        "./pathwayscase:PathwaysCase/pathwayscase:TriageDisposition/pathwayscase:DispositionCode[1]", ns
    )
    return disposition_uid.text


def get_triage_disposition_description(tree):
    disposition_description = tree.find(
        "./pathwayscase:PathwaysCase/pathwayscase:TriageDisposition/pathwayscase:DispositionDescription[1]", ns
    )
    return disposition_description.text


def get_final_disposition_group_cmsid(tree):
    final_disposition_group = tree.find(
        "./pathwayscase:PathwaysCase/pathwayscase:FinalDispositionCMSID/pathwayscase:FinalDispositionCMSID[1]", ns
    )
    return final_disposition_group.text


def get_final_disposition_code(tree):
    final_disposition_code = tree.find(
        "./pathwayscase:PathwaysCase/pathwayscase:FinalDisposition/pathwayscase:DispositionCode[1]", ns
    )
    return final_disposition_code.text


def get_triage_line_data(tree):
    report_texts = []
    symptom_discriminator_uid = ""
    symptom_discriminator_desc_text = ""
    triage_lines = get_triage_lines(tree)
    for triage_line in triage_lines:
        report_texts = add_report_text(triage_line, report_texts)
        care_advice_sd = triage_line.find("pathwayscase:CareAdvice/pathwayscase:SymptomDiscriminator[.!='0']", ns)
        if care_advice_sd is not None:
            symptom_discriminator_uid = care_advice_sd.text
            symptom_discriminator_desc = triage_line.find("pathwayscase:AnswerText", ns)
            symptom_discriminator_desc_text = symptom_discriminator_desc.text
    return report_texts, symptom_discriminator_uid, symptom_discriminator_desc_text.replace('"', "")


def get_triage_lines(tree):
    return tree.findall("./pathwayscase:PathwaysCase/pathwayscase:TriageLineDetails/pathwayscase:TriageLine", ns)


def add_report_text(triage_line, report_text_list):
    report_text = None
    if identify_report_elements_to_include(triage_line) is not None:
        report_text = get_report_text(triage_line)
    if report_text is not None:
        report_text_list.append(report_text)
    return report_text_list


def identify_report_elements_to_include(triage_line):
    return triage_line.find("pathwayscase:IncludeInReport[.='True']", ns)


def get_report_text(triage_line):
    report_text = None
    report_text_element = triage_line.find("pathwayscase:ReportText[.!='']", ns)
    if report_text_element is not None:
        report_text = report_text_element.text
        # TODO may not be needed
        report_text = report_text.replace('"', "")
    return report_text
