from unittest.mock import Mock, patch
import pytest
import string
import psycopg2

from .. import handler
# import integration
# from ...integration import handler

def test_create_db_from_template():

    assert handler.set_up_data_conditions() == True
