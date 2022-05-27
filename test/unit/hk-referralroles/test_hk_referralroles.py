from unittest.mock import patch
import mock
import os
import pytest
from .. import handler

# @mock.patch.dict(os.environ, {"TASK": "referralroles"})
def test_create_query(monkeypatch):
    # monkeypatch.setenv("TASK", "referralroles")
    test_values = {
                "id": 10,
                "name": "Test Data",
                "action": "CREATE"
    }
    query, data = handler.create_query(test_values)
    assert query == """
        insert into pathwaysdos.referralroles (id, name) values (%s, %s)
        returning id, name;
    """
    assert data == (10, "Test Data")


def test_update_query():
    test_values = {
        "id": 10,
        "name": "Test Data",
        "action": "UPDATE"
    }
    query, data = handler.update_query(test_values)
    assert query == """
        update pathwaysdos.referralroles set name = (%s) where id = (%s);
    """
    assert data == ("Test Data", 10)


def test_delete_query():
    test_values = {
        "id": 10,
        "name": "Test Data",
        "action": "DELETE"
    }
    query, data = handler.delete_query(test_values)
    assert query == """
        delete from pathwaysdos.referralroles where id = (%s)
    """
    assert data == (10,)
