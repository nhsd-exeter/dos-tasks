import boto3
import pytest
from moto import mock_s3, mock_secretsmanager
import mock
import sys
import os
import json
import string
import psycopg2
from datetime import datetime

sys.path.append(".")
from .. import handler

class TestHandler:
    filename = "sg.csv"

    db_secrets = {
        "DB_HOST": "localhost",
        "DB_NAME": "pathwaysdos_dev",
        "DB_USER": "postgres",
        "DB_USER_PASSWORD": "postgres",
    }
    s3_bucket_name = "nhsd-texasplatform-service"
    secret_name = "placeholder-secret"

    # example 2001,"Symptom group description","DELETE"
    csv_sg_id = 2001
    csv_sg_desc = "Automated Test"
    csv_sg_action = "REMOVE"


    # # simulates event triggered when putting a file into an s3 bucket
    # def create_s3_event(self, filename: str):
    #     event = {
    #         "Records": [
    #             {
    #                 "eventName": "ObjectCreated:Put",
    #                 "s3": {
    #                     "bucket": {"name": self.s3_bucket_name},
    #                     "object": {"key": filename},
    #                 },
    #             }
    #         ]
    #     }
    #     return event

    # def add_file_to_s3_bucket(self, filename: str):
    #     csv_data = """1,"Name","Update"\n"""
    #     s3 = boto3.resource("s3")
    #     bucket = s3.Bucket(self.s3_bucket_name)
    #     bucket.create(ACL="public-read", CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
    #     bucket.put_object(Body=csv_data, Key=filename)

    # @mock_s3
    # @mock_secretsmanager
    # @mock.patch.dict(os.environ, {"AWS_REGION": "eu-west-2", "SECRETS_NAME": secret_name})
    # @mock.patch("boto3.Session")
    # def test_handler(self, symptomgroup_mock):
    #     # 1. Prep
    #     # create a mock s3 bucket and load file
    #     self.add_file_to_s3_bucket(self.filename)
    #     # create mock event
    #     event = self.create_s3_event(self.filename)
    #     session = boto3.session.Session()
    #     secrets_client = session.client(service_name="secretsmanager", region_name="eu-west-2")
    #     secrets_client.create_secret(Name=self.secret_name, SecretString=json.dumps(self.db_secrets))
    #     # 2. Act
    #     response = handler.request(event=event, context=None)
    #     print(response)
    #     # symptomgroup_mock.symptom_group_service.process_file_data.assert_called_once
    #     # 3. Assert
    #     assert response["message"] == "Symptom groups handler executed successfully"

    # def test_handler_invalid_file_extension(self):
    #     event = self.create_s3_event("sg.c")
    #     with pytest.raises(Exception):
    #         handler.request(event=event, context=None)

    # @mock_s3
    # def test_get_csv_from_s3(self):
    #     # 1.Prep
    #     csv_content = "ABCD"
    #     s3connection = boto3.resource("s3")
    #     bucket = s3connection.Bucket("test-symptomgroups-bucket")
    #     bucket.create(ACL="public-read", CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
    #     bucket.put_object(Body=csv_content, Key=self.filename)

    #     # 2.Act
    #     csv_file = handler.get_csv_from_s3("test-symptomgroups-bucket", self.filename)
    #     # 3.Assert
    #     assert csv_file == csv_content

    # @mock_s3
    # @mock_secretsmanager
    # def test_empty_csv_in_s3(self):

    #     session = boto3.session.Session()
    #     session.client(service_name="secretsmanager", region_name="eu-west-2")
    #     event = self.create_s3_event(self.filename)
    #     response = handler.request(event=event, context=None)
    #     assert response["message"] == "Symptom groups handler execution failed"



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
        # query, data = handler.create_query(csv_dict)
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
        # query, data = handler.update_query(csv_dict)
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
        #  query, data = handler.delete_query(csv_dict)
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


# mock tests below
    @mock.patch("psycopg2.connect")
    def test_record_exists(self, mock_db_connect):
        csv_dict = {}
        csv_dict["csv_sgid"] = str(self.csv_sg_id)
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["action"] = "DELETE"
        csv_dict["csv_zcode"] = None
        mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 1
        assert handler.record_exists(mock_db_connect,csv_dict)

    @mock.patch("psycopg2.connect")
    def test_record_does_not_exist(self, mock_db_connect):
        csv_dict = {}
        csv_dict["csv_sgid"] = str(self.csv_sg_id)
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["action"] = "DELETE"
        csv_dict["csv_zcode"] = None
        mock_db_connect.cursor.return_value.__enter__.return_value.rowcount = 0
        assert not handler.record_exists(mock_db_connect,csv_dict)

    @mock.patch("psycopg2.connect")
    def test_record_does_exception(self, mock_db_connect):
        csv_dict = {}
        csv_dict["csv_sgid"] = str(self.csv_sg_id)
        csv_dict["csv_name"] = self.csv_sg_desc
        csv_dict["action"] = "DELETE"
        csv_dict["csv_zcode"] = None
        mock_db_connect = ""
        with pytest.raises(Exception):
            handler.record_exists(mock_db_connect,csv_dict)

