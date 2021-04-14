# How To Write Problems

<u>To problem author: Please write a JSON file.</u>  

## Format of Problem

Each problem must be defined by JSON file like below.

```json
{
  "DDL": [  // List of strings
    "create table Foo (",
    "    xxx varchar(256) primary key,",
    "    yyy varchar(256),",
    "    zzz varchar(256)",
    ");",
    "create table another ..."
  ],
  "description": [  // Optional
    "Hello!",
    "This is message from writer."
  ],
  "tables": [  // List of tables
    {  // Table information
      "name": "Name of Table",
      "columns": ["names", "of", "columns"],
      "records": [
        ["Hi!", "Foo", "Bar"]
      ]
    }
  ],
  "expected": {  // Expected output
    "columns": ["names", "of", "columns"],
    "records": [
        ["Hi!", "Foo", "Bar"]
    ],
    "order_sensitive": false  // true when using ORDER BY
  }
}
```

> note: Json file name will be used as problem name.

Example: This is a JSON code of sample problem.  
(`problem/sample-1.json`)

```json
{
  "DDL": [
    "create table Students (",
    "    id int primary key,",
    "    name varchar(16)",
    ");"
  ],
  "description": [
    "This is the first problem.",
    "Just select all."
  ],
  "tables": [
    {
      "name": "Students",
      "columns": ["id", "name"],
      "records": [
        [1, "Alice"],
        [2, "Bob"],
        [3, "Charlie"],
        [4, "David"]
      ]
    }
  ],
  "expected": {
    "columns": ["id", "name"],
    "records": [
        [1, "Alice"],
        [2, "Bob"],
        [3, "Charlie"],
        [4, "David"]
    ],
    "order_sensitive": false
  }
}
```

In this case, this table is prepared.

Table: Students
| id | name    |
|----|---------|
| 1  | Alice   |
| 2  | Bob     |
| 3  | Charlie |
| 4  | David   |

And expected output is like this.  
(Now it's same to prepared table)

| id | name    |
|----|---------|
| 1  | Alice   |
| 2  | Bob     |
| 3  | Charlie |
| 4  | David   |

Then user write sql code to solve the problem.  
> Of course it's "`select id, name from Students;`".
