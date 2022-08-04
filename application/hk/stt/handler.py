import xml.etree.ElementTree as ET
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
        # TODO will be a compressed file - rar ? zip?
        # stt_file =
        common.retrieve_file_from_bucket(bucket, filename, event, start)
        # TODO will need to unpack
    except Exception as e:
        logger.log_for_error(env, "Problem {}".format(e))
        message.send_failure_slack_message(event, start)
    finally:
        database.close_connection(event, db_connection)
        common.archive_file(bucket, filename, event, start)
    return task_description + " execution completed"


def process_scenario_files_in_bundle(compressed_file):
    # TODO unpack and iterate over files
    # draft flow
    # get_tree
    # get_symptom_group
    # get_triage_disposition_uid
    # get_triage_disposition_description
    # get_final_disposition_group_cmsid
    # get_final_disposition_code
    # get_triage_line_data
    # build a scenario object for storing in db
    print("TODO")


def get_tree(file):
    tree = ET.parse(file)
    return tree


def get_root(tree):
    return tree.getroot()


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


# def get_report_text(triage_line):
#     report_text_elements_to_include = triage_line.findall("pathwayscase:IncludeInReport[.=='True']",ns)
#     pathwayscase:ReportText[.!='']"
#         if care_advice_sd is not None:
# foreach ($xml->PathwaysCase->TriageLineDetails as $tld) {
#             foreach ($tld->TriageLine as $tl) {
#                 if ($tl->CareAdvice->SymptomDiscriminator != '0') {
#                     $sdUid = $tl->CareAdvice->SymptomDiscriminator;
#                     $sdDescription = $tl->AnswerText;
#                     $sdDescription = trim($sdDescription,'"');
#                 }
#                 if ($tl->IncludeInReport == 'True' && $tl->ReportText != '') {
#                     $reportText[] = (string)$tl->ReportText;
#                 }
#             }
#         }
