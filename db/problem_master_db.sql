--------------------
-- Role Definition
--------------------

-- DROP ROLE USER_NAME;
CREATE ROLE problem WITH
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
CREATE DATABASE problem WITH
	OWNER = problem;
