-- 1.0 Tables

--  1.1 Create import staging table for pharmacies
-- max in text is 65,535 default if not specified is 64000

CREATE TABLE IF NOT EXISTS pathwaysdos.scenariobundles
(
  id bigserial NOT NULL,
  name varchar(255) NOT NULL,
  createdtime TIMESTAMP NOT NULL,
  PRIMARY KEY (id) USING INDEX TABLESPACE pathwaysdos_index_01,
  CONSTRAINT bundlename_unique UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS pathwaysdos.scenarios
(
  id bigserial NOT NULL,
  scenariobundleid integer NOT NULL,
  scenarioid integer NOT NULL,
  symptomgroupid varchar(255) NOT NULL,
  dispositionid integer NOT NULL,
  dispositiongroupid integer,
  symptomdiscriminatorid integer NOT NULL,
  ageid integer NOT NULL,
  genderid integer NOT NULL,
  triagereport varchar ,
  createdtime timestamp with time zone NOT NULL,
  retiredtime timestamp with time zone,
  PRIMARY KEY (id) USING INDEX TABLESPACE pathwaysdos_index_01,
  CONSTRAINT fk_bundle
      FOREIGN KEY(scenariobundleid)
      REFERENCES scenariobundles(id)
);


-- 2.0 Constraints
CREATE UNIQUE INDEX idx_bundle_scenario
ON pathwaysdos.scenarios(scenariobundleid, scenarioid);
