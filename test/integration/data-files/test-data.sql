
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


