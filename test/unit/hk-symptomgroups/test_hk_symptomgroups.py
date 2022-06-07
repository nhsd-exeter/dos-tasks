import pytest
from moto import mock_s3
import mock
import sys
import json
import string
import psycopg2
from datetime import datetime

sys.path.append(".")
from .. import handler
from .. utilities import database, message, s3, secrets

class TestHandler:

    file_path = "application.hk.symptomgroups.handler"

    filename = "test/sg.csv"

    db_secrets = '{"DB_HOST": "localhost","DB_NAME": "pathwaysdos_dev","DB_USER": "postgres","DB_USER_PASSWORD": "postgres"}'

    secret_name = "placeholder-secret"
    bucket = "NoSuchBucket"
    env = "unittest"

    # example 2001,"Symptom group description","DELETE"
    csv_sg_id = 2001
    csv_sg_desc = "Automated Test"
    csv_sg_action = "REMOVE"

    def test_csv_line(self):
        # mimics list of strings produced by csv module
        csv_row = [str(self.csv_sg_id), self.csv_sg_desc, self.csv_sg_action]
        csv_dict = handler.extract_query_data_from_csv(csv_row)
        assert len(csv_dict) == 4
        assert str(csv_dict["csv_sgid"]) == str(self.csv_sg_id)
        assert csv_dict["csv_name"] == str(self.csv_sg_desc)
        assert csv_dict["action"] == str(self.csv_sg_action).upper()
        assert csv_dict["csv_zcode"] is False


    def test_csv_line_lc(self):
        # mimics list of strings produced by csv module
        csv_sg_action = "remove"
        csv_row = [str(self.csv_sg_id), self.csv_sg_desc, csv_sg_action]
        csv_dict = handler.extract_query_data_from_csv(csv_row)
        assert len(csv_dict) == 4
        assert str(csv_dict["csv_sgid"]) == str(self.csv_sg_id)
        assert csv_dict["csv_name"] == str(self.csv_sg_desc)
        assert csv_dict["action"] == str(csv_sg_action).upper()
        assert csv_dict["csv_zcode"] is False


    def test_invalid_csv_line(self):
        # mimics list of strings produced by csv module
        csv_row = [str(self.csv_sg_id), self.csv_sg_desc]
        csv_dict = handler.extract_query_data_from_csv(csv_row)
        assert len(csv_dict) == 0


    def test_no_sgid_csv_line(self):
        # mimics list of strings produced by csv module
        csv_row = ["", self.csv_sg_desc, self.csv_sg_action]
        csv_dict = handler.extract_query_data_from_csv(csv_row)
        assert len(csv_dict) == 4
        assert str(csv_dict["csv_sgid"]) == "None"


    def test_no_sgdesc_csv_line(self):
        # mimics list of strings produced by csv module
        csv_row = [str(self.csv_sg_id), "", self.csv_sg_action]
        csv_dict = handler.extract_query_data_from_csv(csv_row)
        assert len(csv_dict) == 4
        assert str(csv_dict["csv_name"]) == "None"
        assert csv_dict["csv_zcode"] is False


    def test_zcode_sgdesc_csv_line(self):
        # mimics list of strings produced by csv module
        csv_row = [str(self.csv_sg_id), "z2.0 - test", self.csv_sg_action]
        csv_dict = handler.extract_query_data_from_csv(csv_row)
        assert len(csv_dict) == 4
        assert csv_dict["csv_zcode"] is True


    def test_csv_line_exception(self):
        # mimics list of strings produced by csv module action intentionally NOT a string
        csv_row = [str(self.csv_sg_id), self.csv_sg_desc, 1]
        with pytest.raises(Exception):
            handler.extract_query_data_from_csv(csv_row)

    def test_valid_create_action(self):
        csv_dict = {}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "CREATE"
        assert handler.valid_action(False,csv_dict)

    def test_invalid_create_action(self):
        csv_dict = {}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "CREATE"
        assert not handler.valid_action(True,csv_dict)

    def test_valid_update_action(self):
        csv_dict = {}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "UPDATE"
        assert handler.valid_action(True,csv_dict)

    def test_invalid_update_action(self):
        csv_dict = {}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "UPDATE"
        assert not handler.valid_action(False,csv_dict)

    def test_valid_delete_action(self):
        csv_dict = {}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "DELETE"
        assert handler.valid_action(True,csv_dict)

    def test_invalid_delete_action(self):
        csv_dict = {}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "DELETE"
        assert not handler.valid_action(False,csv_dict)

    def test_invalid_action(self):
        csv_dict = {}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "NOSUCH"
        assert not handler.valid_action(True,csv_dict)

    def test_generating_create_query(self):
        create_query_string = """insert into pathwaysdos.symptomgroups(id,name,zcodeexists)
            values (%s, %s, %s)
            returning
            id,
            name,
            zcodeexists;"""
        remove = string.punctuation + string.whitespace

        csv_dict = {}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "CREATE"
        query, data = handler.generate_db_query(csv_dict)
        mapping = {ord(c): None for c in remove}
        assert query.translate(mapping) == create_query_string.translate(mapping),"Query syntax mismatched"
        assert data[0] == csv_dict["csv_sgid"]
        assert data[1] == csv_dict["csv_name"]

    def test_generating_update_query(self):
        update_query_string = """update pathwaysdos.symptomgroups set name = (%s), zcodeexists = (%s)
            where id = (%s);"""
        remove = string.punctuation + string.whitespace

        csv_dict = {}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "UPDATE"
        query, data = handler.generate_db_query(csv_dict)
        mapping = {ord(c): None for c in remove}
        assert query.translate(mapping) == update_query_string.translate(mapping),"Query syntax mismatched"
        assert data[0] == csv_dict["csv_name"]
        assert data[1] == csv_dict["csv_zcode"]
        assert data[2] == csv_dict["csv_sgid"]

    def test_generating_delete_query(self):
        delete_query_string = """delete from pathwaysdos.symptomgroups where id = (%s)"""
        remove = string.punctuation + string.whitespace
        csv_dict = {}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "DELETE"
        query, data = handler.generate_db_query(csv_dict)
        mapping = {ord(c): None for c in remove}
        assert query.translate(mapping) == delete_query_string.translate(mapping),"Query syntax mismatched"
        assert data[0] == csv_dict["csv_sgid"]

    def test_generating_query_with_invalid_action(self):
        csv_dict = {}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "REMOVE"
        with pytest.raises(psycopg2.DatabaseError):
            query, data = handler.generate_db_query(csv_dict)

    @mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
    @mock.patch(f"{file_path}.database.DB.db_set_connection_details", return_value = False)
    def test_db_connect_fails_to_set_connection_details(self,mock_db,mock_send_failure_slack_message):
        start = datetime.utcnow()
        payload = self.generate_event_payload()
        with pytest.raises(ValueError, match='One or more DB Parameters not found in secrets store'):
            handler.connect_to_database("unittest",payload,start)
        mock_db.assert_called_once()
        mock_send_failure_slack_message.assert_called_once()

    @mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
    @mock.patch(f"{file_path}.database.DB.db_set_connection_details", return_value = True)
    def test_db_connect_fail(self,mock_db,mock_send_failure_slack_message):
        start = datetime.utcnow()
        payload = self.generate_event_payload()
        with pytest.raises(psycopg2.InterfaceError):
            handler.connect_to_database("unittest",payload,start)
        mock_send_failure_slack_message.assert_called_once()

    @mock.patch(f"{file_path}.database.DB.db_connect", return_value = "db_connection")
    @mock.patch(f"{file_path}.database.DB.db_set_connection_details", return_value = "True")
    def test_db_connect_succeeds(self,mock_db,mock_connection):
        start = datetime.utcnow()
        payload = self.generate_event_payload()
        handler.connect_to_database("unittest",payload,start)
        assert mock_connection.call_count == 1

    def test_extract_data_from_file_valid_length(self):
        csv_file = """2001,"Automated insert SymptomGroup","INSERT"\n"""
        start = datetime.utcnow()
        event = self.generate_event_payload()
        lines = handler.extract_data_from_file(csv_file, event, start)
        assert len(lines) == 1

    # @mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
    def test_extract_data_from_file_valid_length_multiline(self):
        csv_file = """2001,"Automated insert SymptomGroup","INSERT"\n2001,"Automated update SymptomGroup","UPDATE"\n"""
        start = datetime.utcnow()
        event = self.generate_event_payload()
        lines = handler.extract_data_from_file(csv_file, event, start)
        assert len(lines) == 2

    # @mock.patch(f"{file_path}.message.send_start_message", return_value = None)
    def test_extract_data_from_file_empty_second_line(self):
        csv_file = """2001,"Automated insert SymptomGroup","INSERT"\n\n"""
        start = datetime.utcnow()
        event = self.generate_event_payload()
        lines = handler.extract_data_from_file(csv_file, event, start)
        assert len(lines) == 1

    @mock.patch(f"{file_path}.extract_query_data_from_csv", return_value={"csv_sgid": "2001", "csv_name": "Automated insert SymptomGroup","csv_zcode":"None", "action": "CREATE"})
    def test_extract_data_from_file_three_lines_empty_second_line(self,mock_extract):
        csv_file = """2001,"Automated insert SymptomGroup","INSERT"\n\n\n2001,"Automated update SymptomGroup","UPDATE"\n"""
        start = datetime.utcnow()
        event = self.generate_event_payload()
        lines = handler.extract_data_from_file(csv_file, event, start)
        assert len(lines) == 2
        assert mock_extract.call_count == 2

    @mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
    def test_extract_data_from_file_incomplete_second_line(self,mock_message):
        csv_file = """2001,"Automated insert SymptomGroup","INSERT"\n2002,\n"""
        start = datetime.utcnow()
        event = self.generate_event_payload()
        with pytest.raises(IndexError, match="Unexpected data in csv file"):
            handler.extract_data_from_file(csv_file, event, start)

    @mock.patch(f"{file_path}.extract_query_data_from_csv", return_value={"csv_sgid": "2001", "csv_name": "Automated insert SymptomGroup","csv_zcode":"None", "action": "CREATE"})
    def test_extract_data_from_file_call_count(self,mock_extract):
        csv_file = """2001,"Automated insert SymptomGroup","INSERT"\n2001,"Automated update SymptomGroup","UPDATE"\n"""
        start = datetime.utcnow()
        event = self.generate_event_payload()
        lines = handler.extract_data_from_file(csv_file, event, start)
        assert len(lines) == 2
        assert mock_extract.call_count == len(lines)


    @mock.patch("psycopg2.connect")
    def test_execute_db_query_success(self, mock_db_connect):
        line = """2001,"New Symptom Group","INSERT"\n"""
        data = ("New Symptom Group", "None", 2001)
        values = {}
        values["action"] = "INSERT"
        values['id'] = 2001
        values['name'] = "New Symptom Group"
        mock_db_connect.cursor.return_value.__enter__.return_value = "Success"
        query = """update pathwaysdos.symptomgroups set name = (%s), zcodeexists = (%s)
            where id = (%s);"""
        handler.execute_db_query(mock_db_connect, query, data, line, values)
        mock_db_connect.commit.assert_called_once()
        mock_db_connect.cursor().close.assert_called_once()

    @mock.patch("psycopg2.connect")
    def test_execute_db_query_failure(self, mock_db_connect):
        line = """2001,"New Symptom Group","INSERT"\n"""
        data = ("New Symptom Group", "None", 2001)
        values = {"action":"INSERT","id":2001,"Name":"New Symptom Group"}
        mock_db_connect.cursor.return_value.__enter__.return_value = Exception
        query = """update pathwaysdos.symptomgroups set name = (%s), zcodeexists = (%s)
            where id = (%s);"""
        handler.execute_db_query(mock_db_connect, query, data, line, values)
        mock_db_connect.rollback.assert_called_once()
        mock_db_connect.cursor().close.assert_called_once()

    @mock.patch("psycopg2.connect")
    @mock.patch(f"{file_path}.execute_db_query")
    @mock.patch(f"{file_path}.generate_db_query",return_value=("query", "data"))
    @mock.patch(f"{file_path}.valid_action", return_value=True)
    @mock.patch(f"{file_path}.does_record_exist", return_value=True)
    def test_process_extracted_data_single_record(self,mock_exist,mock_valid_action,mock_generate,mock_execute, mock_db_connect):
        row_data = {}
        csv_dict={}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "DELETE"
        row_data[0]=csv_dict
        handler.process_extracted_data(mock_db_connect, row_data)
        mock_valid_action.assert_called_once()
        mock_exist.assert_called_once()
        mock_generate.assert_called_once()
        mock_execute.assert_called_once()

    @mock.patch("psycopg2.connect")
    @mock.patch(f"{file_path}.execute_db_query")
    @mock.patch(f"{file_path}.generate_db_query",return_value=("query", "data"))
    @mock.patch(f"{file_path}.valid_action", return_value=True)
    @mock.patch(f"{file_path}.does_record_exist", return_value=True)
    def test_process_extracted_data_multiple_records(self,mock_exist,mock_valid_action,mock_generate,mock_execute, mock_db_connect):
        row_data = {}
        csv_dict={}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "DELETE"
        row_data[0]=csv_dict
        row_data[1]=csv_dict
        handler.process_extracted_data(mock_db_connect, row_data)
        assert mock_valid_action.call_count == 2
        assert mock_exist.call_count == 2
        assert mock_generate.call_count == 2
        assert mock_execute.call_count == 2

    @mock.patch("psycopg2.connect")
    # @mock.patch(f"{file_path}.does_record_exist", return_value=True)
    def test_process_extracted_data_error_check_exists_fails(self,mock_db_connect):
        row_data = {}
        csv_dict = {}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "DELETE"
        row_data[0]=csv_dict
        mock_db_connect = ""
        with pytest.raises(Exception):
            handler.process_extracted_data(mock_db_connect, row_data)

    @mock.patch("psycopg2.connect")
    @mock.patch(f"{file_path}.does_record_exist", return_value=True)
    def test_process_extracted_data_error_check_exists_passes(self,mock_exists,mock_db_connect):
        row_data = {}
        csv_dict = {}
        csv_dict["csv_sgid"] = self.csv_sg_id
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["csv_zcode"] = False
        csv_dict["action"] = "DELETE"
        row_data[0]=csv_dict
        mock_db_connect = ""
        with pytest.raises(Exception):
            handler.process_extracted_data(mock_db_connect, row_data)
        assert mock_exists.call_count == 1

    @mock.patch(f"{file_path}.s3.S3.get_object", return_value = None)
    def test_get_csv_from_s3(self, mock_s3):
        start = datetime.utcnow()
        event = self.generate_event_payload()
        csv_file = handler.retrieve_file_from_bucket(self.bucket, self.filename,event,start)
        assert csv_file == None

    @mock.patch("psycopg2.connect")
    def test_record_exists_true(self, mock_db_connect):
        csv_dict = {}
        csv_dict["csv_sgid"] = str(self.csv_sg_id)
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["action"] = "DELETE"
        csv_dict["csv_zcode"] = None
        mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 1
        assert handler.does_record_exist(mock_db_connect,csv_dict)

    @mock.patch("psycopg2.connect")
    def test_does_record_exist_false(self, mock_db_connect):
        csv_dict = {}
        csv_dict["csv_sgid"] = str(self.csv_sg_id)
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["action"] = "DELETE"
        csv_dict["csv_zcode"] = None
        mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 0
        assert not handler.does_record_exist(mock_db_connect,csv_dict)

    @mock.patch("psycopg2.connect")
    def test_does_record_exist_exception(self, mock_db_connect):
        csv_dict = {}
        csv_dict["csv_sgid"] = str(self.csv_sg_id)
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["action"] = "DELETE"
        csv_dict["csv_zcode"] = None
        mock_db_connect = ""
        with pytest.raises(Exception):
            handler.does_record_exist(mock_db_connect,csv_dict)

    @mock.patch(f"{file_path}.message.send_success_slack_message", return_value = None)
    @mock.patch(f"{file_path}.s3.S3.delete_object", return_value = None)
    @mock.patch(f"{file_path}.s3.S3.copy_object", return_value = None)
    @mock.patch("psycopg2.connect")
    def test_cleanup(self,mock_db_connect,mock_s3_copy,mock_s3_delete,mock_message):
        start = datetime.utcnow()
        event = self.generate_event_payload()
        # mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 0
        handler.cleanup(mock_db_connect, self.bucket, self.filename, event, start)
        mock_s3_copy.assert_called_once()
        mock_s3_delete.assert_called_once()
        mock_message.assert_called_once()
        mock_db_connect.close.assert_called_once()

    @mock.patch(f"{file_path}.database.DB.db_set_connection_details", return_value = True)
    @mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
    @mock.patch(f"{file_path}.message.send_start_message", return_value = None)
    @mock.patch(f"{file_path}.s3.S3.get_object", return_value = None)
    def test_handler_exception(self,mock_db,mock_failure_message,mock_message_start,mock_s3):
        payload = self.generate_event_payload()
        with pytest.raises(Exception):
            with mock.patch(secrets.__name__ + '.SECRETS.get_secret_value', return_value = json.dumps(self.db_secrets)):
                handler.request(event=payload, context=None)

    #
    @mock.patch("psycopg2.connect")
    @mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
    @mock.patch(f"{file_path}.message.send_success_slack_message", return_value = None)
    @mock.patch(f"{file_path}.s3.S3.delete_object", return_value = None)
    @mock.patch(f"{file_path}.s3.S3.copy_object", return_value = None)
    @mock.patch(f"{file_path}.execute_db_query")
    @mock.patch(f"{file_path}.does_record_exist", return_value=True)
    @mock.patch(f"{file_path}.s3.S3.get_object", return_value="""2001,"New Symptom Group","UPDATE"\n""")
    @mock.patch(f"{file_path}.database.DB.db_set_connection_details", return_value = True)
    @mock.patch(f"{file_path}.message.send_start_message")
    def test_handler_pass(self,mock_send_start_message,mock_db_details,mock_get_object,
    mock_does_record_exist,mock_execute_db_query,mock_copy_object,mock_delete_object,mock_send_success_slack_message,mock_send_failure_slack_message,mock_db_connect):
        payload = self.generate_event_payload()
        with mock.patch(secrets.__name__ + '.SECRETS.get_secret_value', return_value = 'SecretString=' + json.dumps(self.db_secrets)):
            handler.request(event=payload, context=None)
            mock_send_start_message.assert_called_once()
            mock_get_object.assert_called_once()
            mock_copy_object.assert_called_once()
            mock_delete_object.assert_called_once()
            mock_send_success_slack_message.assert_called_once()
            mock_does_record_exist.assert_called_once()
            mock_execute_db_query.assert_called_once
            mock_send_failure_slack_message.assert_not_called()

    @mock.patch("psycopg2.connect")
    @mock.patch(f"{file_path}.message.send_failure_slack_message", return_value = None)
    @mock.patch(f"{file_path}.message.send_success_slack_message", return_value = None)
    @mock.patch(f"{file_path}.s3.S3.delete_object", return_value = None)
    @mock.patch(f"{file_path}.s3.S3.copy_object", return_value = None)
    @mock.patch(f"{file_path}.does_record_exist", return_value=False)
    @mock.patch(f"{file_path}.s3.S3.get_object", return_value="""2001,"New Symptom Group","UPDATE"\n""")
    @mock.patch(f"{file_path}.database.DB.db_set_connection_details", return_value = True)
    @mock.patch(f"{file_path}.message.send_start_message")
    def test_handler_fail(self,mock_send_start_message,mock_db_details,mock_get_object,
    mock_does_record_exist,mock_copy_object,mock_delete_object,mock_send_failure_slack_message,mock_send_success_slack_message,mock_db_connect):
        payload = self.generate_event_payload()
        with mock.patch(secrets.__name__ + '.SECRETS.get_secret_value', return_value = 'SecretString=' + json.dumps(self.db_secrets)):
            handler.request(event=payload, context=None)
            # mock_send_start_message.assert_called_once()
            assert mock_send_start_message.call_count == 1
            mock_get_object.assert_called_once()
            mock_send_failure_slack_message.assert_called_once()
            mock_copy_object.assert_called_once()
            mock_delete_object.assert_called_once()
            mock_send_success_slack_message.assert_not_called()
            mock_does_record_exist.assert_called_once()

    def generate_event_payload(self):
        return {"filename": self.filename, "env": self.env, "bucket": self.bucket}
