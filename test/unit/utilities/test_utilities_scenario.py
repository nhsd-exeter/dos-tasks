import pytest

def test_scenario():
    from ..scenario import Scenario
    template_scenario = Scenario(
            "A",
            4,
            5,
            6,
            7,
            "H",
            8,
            1,
            2
        )
    assert template_scenario.bundle_id == "A"
    assert template_scenario.scenario_id   == 4
    assert template_scenario.symptom_group_id  == 5
    assert template_scenario.disposition_id == 6
    assert template_scenario.disposition_group_id == 7
    assert template_scenario.triage_report == "H"
    assert template_scenario.symptom_discriminator_id == 8
    assert template_scenario.age_id == 1
    assert template_scenario.gender_id == 2
