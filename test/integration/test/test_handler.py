from unittest.mock import Mock, patch
import pytest
import string
import psycopg2

from .. import handler
# from utilities import secrets,common
# import integration
# from ...integration import handler

def test_create_db_from_template():
    user = "usr"
    db_master_password = "db_pass"
    db_host = "db_host"
    db_port = 5432
    db_name = "integration"
    assert handler.create_db_from_template(user, db_master_password, db_host, db_port, db_name) == True
