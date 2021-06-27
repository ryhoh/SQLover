--------------------
-- Sequence Definition
--------------------

-- DROP SEQUENCE public.problems_id_seq;
CREATE SEQUENCE public.problems_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- DROP SEQUENCE public.results_id_seq;
CREATE SEQUENCE public.results_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- DROP SEQUENCE public.users_id_seq;
CREATE SEQUENCE public.users_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;


--------------------
-- Table Definition
--------------------

-- DROP TABLE public.credential;
CREATE TABLE public.credential (
	value varchar(255) NOT NULL,
	"type" varchar(31) NOT NULL,
	CONSTRAINT credential_pk PRIMARY KEY (type)
);

-- DROP TABLE public.problems;
CREATE TABLE public.problems (
	id serial NOT NULL,
	"name" varchar(64) NOT NULL,
	CONSTRAINT problems_pk PRIMARY KEY (id),
	CONSTRAINT problems_un UNIQUE (name)
);

-- DROP TABLE public.users
CREATE TABLE public.users (
	id serial NOT NULL,
	"name" varchar(32) NOT NULL,
	passwd bytea NOT NULL,
	email varchar(255) NOT NULL,
	is_active bool NOT NULL DEFAULT false,
	CONSTRAINT users_email_un UNIQUE (email),
	CONSTRAINT users_name_un UNIQUE (name),
	CONSTRAINT users_pk PRIMARY KEY (id)
);
CREATE UNIQUE INDEX users_name_idx ON public.users USING btree (name);

-- DROP TABLE public.results;
CREATE TABLE public.results (
	id serial NOT NULL,
	problem_id int4 NOT NULL,
	user_id int4 NOT NULL,
	cleared bool NOT NULL,
	CONSTRAINT results_pk PRIMARY KEY (id),
	CONSTRAINT results_problem_id_user_id_un UNIQUE (problem_id, user_id),
	CONSTRAINT results_fk_problems FOREIGN KEY (problem_id) REFERENCES public.problems(id) ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT results_fk_users FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE UNIQUE INDEX results_problem_id_user_id_idx ON public.results USING btree (problem_id, user_id);


--------------------
-- Data Insertion
--------------------

INSERT INTO public.credential (value,"type") VALUES
	 ('cf6ecd429e05b2ce17a66b4e06c1e467ac335bae0962c516f42a8bdb69c754d1','JWT_secret'),
	 ('a5e98f4f1e16ed6400e62cdc0c955132-1d8af1f4-d3c77544','mailgun_api_key');
	 
INSERT INTO public.problems ("name") VALUES
	 ('entry-1'),
	 ('sample-1');
	 
INSERT INTO public.users (name,passwd,email,is_active) VALUES
	 ('testuser', decode(E'$2b$12$0qLWitw/XJyqf/j/1D42/uVMEoqmkgQfFu84OUjhqJ2eELtQC7S1e', 'escape'),'test@shirosha2.example.com',true);


--------------------
-- Permissions
--------------------

GRANT SELECT ON TABLE public.credential TO web;
GRANT INSERT, SELECT ON TABLE public.problems TO web;
GRANT USAGE ON SEQUENCE public.problems_id_seq TO web;
GRANT INSERT, SELECT, UPDATE ON TABLE public.results TO web;
GRANT USAGE ON SEQUENCE public.results_id_seq TO web;
GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.users TO web;
GRANT USAGE ON SEQUENCE public.users_id_seq TO web;
