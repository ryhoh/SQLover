--------------------
-- Role Definition
--------------------

-- DROP ROLE USER_NAME;
CREATE ROLE web WITH
	NOSUPERUSER
	NOCREATEDB
	NOCREATEROLE
	INHERIT
	LOGIN
	NOREPLICATION
	NOBYPASSRLS
	CONNECTION LIMIT -1;


--------------------
-- DataBase Definition
--------------------
CREATE DATABASE sqlabo WITH
	OWNER = web;
