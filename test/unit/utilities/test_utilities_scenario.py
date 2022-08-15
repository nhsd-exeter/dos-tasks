import pytest

def test_scenario():
    from ..scenario import Scenario
    template_scenario = Scenario(
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L"
        )
    assert template_scenario.pathways_release_id == "A"
    assert template_scenario.file_name   == "B"
    assert template_scenario.symptom_group  == "C"
    assert template_scenario.triage_disposition_uid == "D"
    assert template_scenario.triage_disposition_description == "E"
    assert template_scenario.final_disposition_group_cmsid == "F"
    assert template_scenario.final_disposition_code == "G"
    assert template_scenario.report_texts == "H"
    assert template_scenario.symptom_discriminator_uid == "I"
    assert template_scenario.symptom_discriminator_desc_text == "J"
    assert template_scenario.age_id == "K"
    assert template_scenario.gender_id == "L"
