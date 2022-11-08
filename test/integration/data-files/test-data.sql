
-- for symptomgroup integration testing
-- create record for hk job to update later
insert into symptomgroups (id, name, zcodeexists)
values ('2001', 'TBC', False);
-- create record for hk job to delete later
insert into symptomgroups (id, name, zcodeexists)
values ('2002', 'Integration Test - Delete', False);
--
--for referralroles integration testing
-- create record for referralroles job to update later
insert into pathwaysdos.referralroles (id, name)
values ('2001','TBC');
-- create record for referralroles job to delete later
insert into pathwaysdos.referralroles (id, name)
values ('2002','Integration Test Delete');
--
--for servicetypes integration testing
-- create record for servicetypes job to update later
insert into pathwaysdos.servicetypes (id, name, nationalranking, searchcapacitystatus, capacitymodel, capacityreset)
values ('2001','TBC',8,True,'n/a','interval');
-- create record for servicetypes job to delete later
insert into pathwaysdos.servicetypes (id, name, nationalranking, searchcapacitystatus, capacitymodel, capacityreset)
values ('2002','Integration Test Delete',8,True,'n/a','interval');
--
--for symptomdiscriminators integration testing
-- create record for symptomdiscriminators job to update later
insert into pathwaysdos.symptomdiscriminators (id,description)
values (20001,'TBC');
-- create record for symptomdiscriminators job to delete later
insert into pathwaysdos.symptomdiscriminators (id,description)
values (20002,'Integration Test Delete');
--
--for symptomgroupdiscriminators integration testing
-- create record to symptomdiscriminators job to delete later
insert into pathwaysdos.symptomgroupsymptomdiscriminators (symptomgroupid,symptomdiscriminatorid)
values (1121,4017);
--
--for symptomdiscriminatorsynonyms integration testing
-- create record to symptomdiscriminatorsynonyms job to delete later
insert into pathwaysdos.symptomdiscriminatorsynonyms (name, symptomdiscriminatorid)
values ('Integration test delete','11009');
