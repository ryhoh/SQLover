package judge

import (
	"os"
	"reflect"
	"testing"
)

// var LOCAL_DB_URL = "postgresql://web:web@localhost:54320/sandbox?sslmode=disable"

func TestExecuteSQL_Simple(t *testing.T) {
	var (
		expected_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{4, "David"},
		}
		actual_result       = SQLRows{}
		sql_execute_request = SQLExecuteRequest{
			create_sql: `create table Students (
				id int primary key,
			    name varchar(16)
			);`,
			insert_sql: `insert into Students values
				(1, 'Alice'),
				(2, 'Bob'),
				(3, 'Charlie'),
				(4, 'David')
			;`,
			select_sql: "select * from Students;",
		}
		sql_execute_result = SQLExecuteResult{
			expected_result: &expected_result,
			actual_result:   &actual_result,
			order_strict:    false,
		}
	)
	os.Setenv("SANDBOX_DB_URL", LOCAL_DB_URL)

	err := executeSQL(&sql_execute_request, &sql_execute_result)
	if err != nil {
		t.Errorf("expected nil but given %#v", err)
	}
	if !reflect.DeepEqual(sql_execute_result.expected_result, sql_execute_result.actual_result) {
		t.Errorf("expected\n%#v\nbut given\n%#v\n", sql_execute_result.expected_result, sql_execute_result.actual_result)
	}
}

func TestExecuteSQL_VariousTypes(t *testing.T) {
	var (
		expected_result = SQLRows{
			{1, "A", "2019-03-01 10:00:00"},
			{2, "B", "2019-03-01 11:00:00"},
			{3, "C", "2019-03-01 12:00:00"},
			{4, "D", "2019-03-01 13:00:00"},
		}
		actual_result       = SQLRows{}
		sql_execute_request = SQLExecuteRequest{
			create_sql: `create table Students (
				id int primary key,
			    c char(1),
				ts timestamp with time zone
			);`,
			insert_sql: `insert into Students values
				(1, 'A', '2019-03-01 10:00:00'),
				(2, 'B', '2019-03-01 11:00:00'),
				(3, 'C', '2019-03-01 12:00:00'),
				(4, 'D', '2019-03-01 13:00:00')
			;`,
			select_sql: "select * from Students;",
		}
		sql_execute_result = SQLExecuteResult{
			expected_result: &expected_result,
			actual_result:   &actual_result,
			order_strict:    false,
		}
	)
	os.Setenv("SANDBOX_DB_URL", LOCAL_DB_URL)

	err := executeSQL(&sql_execute_request, &sql_execute_result)
	if err != nil {
		t.Errorf("expected nil but given %#v", err)
	}
}
