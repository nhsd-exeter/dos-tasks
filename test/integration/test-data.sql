-- for symptomgroup integration testing
insert into symptomgroups (id, name, zcodeexists)
values ('9999', 'Int Test SG', False);

update symptomgroups sg
set name = 'tbc'
where sg.id = 1226 and name = 'Dental Problems'

--
