-- for symptomgroup integration testing
-- create record for hk job to update later
insert into symptomgroups (id, name, zcodeexists)
values ('2001', 'TBC', False);
-- create record for hk job to delete later
insert into symptomgroups (id, name, zcodeexists)
values ('2002', 'Integration Test - Delete', False);
--
