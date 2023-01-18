use testdb;

CREATE TABLE temp(
    ID INT NOT NULL AUTO_INCREMENT,
    firstName VARCHAR(20) NOT NULL,
    lastName VARCHAR(20) NOT NULL,
    PRIMARY KEY (ID)
);

INSERT INTO temp(firstName, lastName)
VALUES("John", "Downing"), ("Emma", "Smith");

CREATE USER 'newuser'@'%' IDENTIFIED BY '777';

GRANT ALL PRIVILEGES ON testdb.* to 'newuser'@'%'