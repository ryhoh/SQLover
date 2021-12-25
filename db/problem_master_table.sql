create table students (
       id int primary key,
       name varchar(16) unique,
       age int,
       gender char(1)
);

create table livesin (
       student_id int primary key,
       place varchar(16),
       
       foreign key(student_id) references Students(id)
);

INSERT INTO students
VALUES
       (1, 'Alice', 16, 'F'),
       (2, 'Bob', 18, 'M'),
       (3, 'Charlie', 15, 'M'),
       (4, 'David', 23, 'M'),
       (5, 'Emilia', 29, 'F'),
       (6, 'François', 24, 'M'),
       (7, 'Günter', 16, 'M'),
       (8, 'Hàoyǔ', 21, 'M'),
       (9, 'Iori', 20, 'F');


INSERT INTO LivesIn
VALUES
       (1, 'Detroit'),
       (2, 'Birmingham'),
       (3, 'Canberra'),
       (4, 'Birmingham');
