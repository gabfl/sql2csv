CREATE TABLE some_pg_table (
    id SERIAL primary key,
    some_int integer not null,
    some_str text not null,
    some_date timestamp without time zone
);

INSERT INTO some_pg_table (some_int, some_str, some_date) VALUES (12, 'hello world', '2018-12-01 12:23:12');
INSERT INTO some_pg_table (some_int, some_str, some_date) VALUES (15, 'hello', '2018-12-05 12:18:12');
INSERT INTO some_pg_table (some_int, some_str, some_date) VALUES (18, 'world', '2018-12-008 12:17:12');
