use mysql;

drop user if exists 'derivatex_backend'@'localhost';
create user 'derivatex_backend'@'localhost' identified by 'qwerty123';

drop database if exists derivatex;
drop database if exists external;
drop database if exists test;

create database derivatex;
create database external;
create database test;

grant all privileges on derivatex.* to 'derivatex_backend'@'localhost';
grant all privileges on external.* to 'derivatex_backend'@'localhost';
grant all privileges on test.* to 'derivatex_backend'@'localhost';

flush privileges;
