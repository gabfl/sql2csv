CREATE TABLE some_mysql_table (
    id int NOT NULL AUTO_INCREMENT,
    some_int int DEFAULT NULL,
    some_str varchar(255) DEFAULT NULL,
    some_date datetime DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB;

INSERT INTO some_mysql_table (some_int, some_str, some_date) VALUES (12, 'hello world', '2018-12-01 12:23:12');
INSERT INTO some_mysql_table (some_int, some_str, some_date) VALUES (15, 'hello', '2018-12-05 12:18:12');
INSERT INTO some_mysql_table (some_int, some_str, some_date) VALUES (18, 'world', '2018-12-008 12:17:12');
