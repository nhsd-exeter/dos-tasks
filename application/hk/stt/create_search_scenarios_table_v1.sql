-- 1.0 Tables

--  1.1 Create import staging table for pharmacies
-- max in text is 65,535 default if not specified is 64000

CREATE TABLE IF NOT EXISTS pathwaysdos.searchscenariobundles
(
  id INTEGER PRIMARY KEY
  bundlename varchar(255) NOT NULL
  createdtime TIMESTAMP NOT NULL,
);


CREATE TABLE IF NOT EXISTS pathwaysdos.searchscenarios
(
  id bigserial NOT NULL,
  releaseid varchar(255) NOT NULL,
  scenarioid varchar(255) NOT NULL,
  symptomgroup_uid varchar(255),
  triagedispositionuid varchar(255),
  triage_disposition_description varchar(255),
  final_disposition_group_cmsid  varchar(255),
  final_disposition_code varchar(255),
  report_texts varchar,
  symptom_discriminator_uid varchar(255),
  symptom_discriminator_desc_text varchar ,
  scenariofilename varchar(255) NOT NULL,
  scenariofile text,
  created_on TIMESTAMP NOT NULL,
  retired BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (id) USING INDEX TABLESPACE pathwaysdos_index_01
);


-- 2.0 Constraints
CREATE UNIQUE INDEX idx_bundle_scenario
ON pathwaysdos.searchscenarios(releaseid, scenarioid);

-- 3.0 Indexes

-- 3.1 Create import indexes for retrieval by postcode and CCG organisation
-- CREATE INDEX IF NOT EXISTS IDX_groupserviceimports_uid ON pathwaysdos.groupserviceimports(uid) TABLESPACE pathwaysdos_index_01;

-- 4.0 Data statements
-- Not applicable

-- 5.0 Permissions

--  5.1 Grant permissions on the new tables

\set database_name `echo "$DB_NAME"`

GRANT USAGE ON SCHEMA pathwaysdos TO pathwaysdos_auth_grp;
GRANT USAGE ON SCHEMA pathwaysdos TO pathwaysdos_read_grp;
GRANT USAGE ON SCHEMA extn_pgcrypto TO pathwaysdos_read_grp;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA extn_pgcrypto TO pathwaysdos_read_grp;
GRANT USAGE ON SCHEMA pathwaysdos TO pathwaysdos_write_grp;

GRANT CONNECT ON DATABASE :database_name  TO pathwaysdos_auth_grp;
GRANT CONNECT ON DATABASE :database_name  TO pathwaysdos_read_grp;
GRANT CONNECT ON DATABASE :database_name  TO pathwaysdos_write_grp;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA pathwaysdos TO pathwaysdos_write_grp;
-- pathwaysdos_auth roles access permissions - for now, we'll allow read access to all other tables
REVOKE UPDATE, INSERT, DELETE ON ALL tables IN SCHEMA pathwaysdos FROM pathwaysdos_auth_grp;
GRANT SELECT ON ALL tables IN SCHEMA pathwaysdos TO pathwaysdos_auth_grp;
GRANT UPDATE (email, password, badpasswordcount, badpasswordtime, lastlogintime, validationtoken, status, createdtime) ON TABLE pathwaysdos.users TO pathwaysdos_auth_grp;

-- For now, we'll add select on all to pathwaysdos, but later we'll want to restrict further if possible
GRANT SELECT ON ALL tables IN SCHEMA pathwaysdos TO pathwaysdos_read_grp;
GRANT UPDATE, INSERT, DELETE ON ALL tables IN SCHEMA pathwaysdos TO pathwaysdos_write_grp;
REVOKE UPDATE ON TABLE pathwaysdos.users FROM pathwaysdos_write_grp;
GRANT UPDATE(id, username, firstname, lastname,email, password, phone,status,createdtime,lastlogintime,homeorganisation, accessreason,approvedby,approveddate, validationtoken) ON TABLE pathwaysdos.users TO pathwaysdos_write_grp;

--GRANT TRUNCATE ON pathwaysdos.searchscenarios TO pathwaysdos;
