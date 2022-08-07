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
DROP DATABASE IF EXISTS sandbox;
CREATE DATABASE sandbox WITH
	OWNER = web;
