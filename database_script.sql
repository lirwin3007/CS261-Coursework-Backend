SET GLOBAL validate_password_policy=LOW;
create database if not exists derivatex;
create database if not exists external;
create user if not exists 'test_user'@'localhost' identified by 'qwerty123';
GRANT ALL PRIVILEGES ON derivatex.* TO 'test_user'@'localhost';
flush privileges;
