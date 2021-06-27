--------------------
-- Role Definition
--------------------

-- DROP ROLE web;
CREATE ROLE web WITH 
	NOSUPERUSER
	NOCREATEDB
	NOCREATEROLE
	NOINHERIT
	LOGIN
	NOREPLICATION
	NOBYPASSRLS
	CONNECTION LIMIT -1;

--------------------
-- DataBase Definition
--------------------
CREATE DATABASE sandbox WITH
	OWNER = web;
