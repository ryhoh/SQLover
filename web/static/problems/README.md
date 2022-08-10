# How To Write Problems

<u>To problem writer: Please write a JSON file.</u>  

## Format of JSON

Each problem must be defined by JSON file like below.

```json
{
  "DDL": [  // Required, List of strings
    "create table Foo (",
    "    xxx varchar(256) primary key,",
    "    yyy varchar(256),",
    "    zzz varchar(256)",
    ");",
    "create table another ..."
  ],
  "description": [  // Required
    "Hello!",
    "This is message from writer."
  ],
  "description_jp": [  // Optional
    "こんにちは。",
    "日本語の説明を書くこともできます。"
  ],
  "tables": [  // Required, List of tables
    {  // Table information
      "name": "Name of Table",
      "columns": ["names", "of", "columns"],
      "records": [
        ["Hi!", "Foo", "Bar"]
      ]
    }
  ],
  "expected": {  // Required, Expected output
    "columns": ["names", "of", "columns"],
    "records": [
        ["Hi!", "Foo", "Bar"]
    ],
    "order_sensitive": false  // Required, true when using ORDER BY
  },
  "writer": "your_name_here"  // Required
}
```

> note: The JSON file name will also be used as the problem name.

Example: This is a JSON of sample problem.  
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
  "description_jp": [
    "最初の問題です。",
    "表全体をそのまま出力してください。"
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
  },
  "writer": "ryhoh"
}
```

In this case, this table will be given.

Table: Students
| id | name    |
|----|---------|
| 1  | Alice   |
| 2  | Bob     |
| 3  | Charlie |
| 4  | David   |

And the expected output looks like below. 
(This time, it is the same as the table we were given)

| id | name    |
|----|---------|
| 1  | Alice   |
| 2  | Bob     |
| 3  | Charlie |
| 4  | David   |

The user then writes the SQL code which solves the problem.  
> Of course, the answer is  "`select id, name from Students;`".
