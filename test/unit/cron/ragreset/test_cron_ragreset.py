from unittest.mock import patch
import pytest
# import string
# import psycopg2

from .. import handler
# from utilities import secrets,common

file_path = "application.cron.ragreset.handler"

expected_update_query = """
        update pathwaysdos.servicecapacities
        set
            notes = (%s),
            modifiedby = (%s),
            modifiedbyid = (%s),
            modifieddate = now(),
            capacitystatusid = (%s),
            resetdatetime = null
        where id in (
            select sercap.id from pathwaysdos.servicecapacities sercap
            join pathwaysdos.services s
            on s.id = sercap.serviceid
            join pathwaysdos.servicetypes st
            on s.typeid = st.id
            where
                sercap.capacitystatusid <> (%s)
                and st.capacityreset = (%s)
                and now() >= sercap.resetdatetime
                and s.typeid not in (%s,%s)
                )
        returning
        *
    """

expected_service_query = """select uid, name, typeid, parentid
            from services
            where id = %s
    """

expected_parent_uid_query = """select ser.id as parentid, ser.uid as parentuid
            from services as ser
            where ser.id = (select parentid from services where id = %s);
    """

expected_region_name_query = """select s.uid, s.name,
            (with recursive tree AS(
            select s.id,s.uid,s.parentid,s.name, 1 AS lvl FROM services s where s.id = %s
            union all
            select s.id,s.uid,s.parentid,s.name, lvl+1 AS lvl
            from services s
            inner join tree t ON s.id = t.parentid)
            select name from tree order by lvl desc limit 1) AS dosregion
        from services s
        where s.id = %s
    """

@patch("psycopg2.connect")
@patch(f"{file_path}.cron_common.cron_cleanup")
@patch(f"{file_path}.database.execute_resultset_query", return_value="" )
@patch(f"{file_path}.database.connect_to_database", return_value="db_connection")
def test_handler_pass(mock_db_details, mock_update_query, mock_cleanup, mock_db_connect):
    """Test top level request calls downstream functions - success"""
    payload = {"id": "ABC", "time": "DEF"}
    handler.request(event=payload, context=None)
    mock_cleanup.assert_called_once()
    mock_db_details.assert_called_once()
    mock_update_query.assert_called_once()


def test_generate_update_query():
    update_query, data  = handler.generate_update_query()
    assert update_query == expected_update_query
    assert len(data) == 8
    assert data[0] == ""
    assert data[1] == handler.modified_by
    assert data[2] == handler.modified_by_id
    assert data[3] == handler.new_status
    assert data[4] == handler.new_status
    assert data[5] == handler.interval_type
    assert data[6] == handler.ignore_org_types[0]
    assert data[7] == handler.ignore_org_types[1]


def test_generate_service_query():
    service_id = 999
    query, data  = handler.generate_service_query(service_id)
    assert ''.join(query.split()) == ''.join(expected_service_query.split())
    assert query == expected_service_query
    assert len(data) == 1
    assert data[0] == service_id

def test_parent_uid_query():
    service_id = 999
    query, data  = handler.generate_parent_uid_query(service_id)
    assert ''.join(query.split()) == ''.join(expected_parent_uid_query.split())
    assert len(data) == 1
    assert data[0] == service_id

def test_generate_region_name_query():
    service_id = 999
    query, data  = handler.generate_region_name_query(service_id)
    assert ''.join(query.split()) == ''.join(expected_region_name_query.split())
    assert len(data) == 2
    assert data[0] == service_id
    assert data[1] == service_id

# TODO may need to revisit
@patch("psycopg2.connect")
def test_log_updated_services(mock_db_connect):
    row_one = {"serviceid": 1,"service_name": "Mustang"}
    row_two = {"serviceid": 2,"service_name": "Mustang"}
    updated_services = [row_one,row_two]
    handler.log_updated_services('mockenv', mock_db_connect,updated_services)

@patch("psycopg2.connect")
def test_log_updated_services_keyerror(mock_db_connect):
    row_one = {"service_name": "Mustang"}
    row_two = {"service_name": "Mustang"}
    updated_services = [row_one,row_two]
    with pytest.raises(KeyError):
        handler.log_updated_services('mockenv', mock_db_connect,updated_services)

@patch("psycopg2.connect")
@patch(f"{file_path}.log_updated_services", return_value="" )
@patch(f"{file_path}.database.execute_resultset_query", side_effect=KeyError)
@patch(f"{file_path}.generate_update_query", side_effect=[{1:'',2:''}])
def test_reset_rag_status(mock_update_query, mock_execute, mock_log, mock_db_connect):
    with pytest.raises(KeyError):
        handler.reset_rag_status('mockenv', mock_db_connect)
