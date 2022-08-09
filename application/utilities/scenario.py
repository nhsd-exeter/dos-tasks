class Scenario:
    def __init__(
        self,
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
    ):
        self.pathways_release_id = pathways_release_id
        self.file_name = file_name
        self.symptom_group = symptom_group
        self.triage_disposition_uid = triage_disposition_uid
        self.triage_disposition_description = triage_disposition_description
        self.final_disposition_group_cmsid = final_disposition_group_cmsid
        self.final_disposition_code = final_disposition_code
        self.report_texts = report_texts
        self.symptom_discriminator_uid = symptom_discriminator_uid
        self.symptom_discriminator_desc_text = symptom_discriminator_desc_text
