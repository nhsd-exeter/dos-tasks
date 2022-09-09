class Scenario:
    def __init__(
        self,
        bundle_id,
        scenario_id,
        symptom_group_id,
        disposition_id,
        disposition_group_id,
        triage_report,
        symptom_discriminator_id,
        age_id,
        gender_id,
    ):
        self.bundle_id = bundle_id
        self.scenario_id = scenario_id
        self.symptom_group_id = symptom_group_id
        self.disposition_id = disposition_id
        self.disposition_group_id = disposition_group_id
        self.triage_report = triage_report
        self.symptom_discriminator_id = symptom_discriminator_id
        self.age_id = age_id
        self.gender_id = gender_id
