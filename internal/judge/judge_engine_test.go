package judge

import (
	"os"
	"reflect"
	"strings"
	"testing"

	. "sqlpuzzlers/internal/common"
)

func TestReadVersion(t *testing.T) {
	version, err := ReadVersion()
	if err != nil {
		t.Errorf("expected nil but given %#v", err)
	}

	if strings.Split(version, " ")[0] != "PostgreSQL" {
		t.Errorf("invalid version given %#v", version)
	}
}

func TestJudgeMain(t *testing.T) {
	var (
		actual_result = SQLRows{
			{int64(1), "Alice"},
			{int64(2), "Bob"},
			{int64(3), "Charlie"},
			{int64(4), "Dave"},
		}
		actual_columns    = []string{"id", "name"}
		expected_json_map = map[string]interface{}{
			"result":         "AC",
			"wrong_line":     -1,
			"answer_columns": actual_columns,
			"answer_records": actual_result,
		}
	)

	retval, err := JudgeMain("select * from Students;", "../../../../../web/static/problems/sample-1")
	if err != nil {
		t.Errorf("expected nil but given %#v", err)
	}
	actual_json_map := *retval
	if expected_json_map["result"] != actual_json_map["result"] {
		t.Errorf("expected\n%#v\nbut given\n%#v\n", expected_json_map["result"], actual_json_map["result"])
	}
	if expected_json_map["wrong_line"] != actual_json_map["wrong_line"] {
		t.Errorf("expected\n%#v\nbut given\n%#v\n", expected_json_map["wrong_line"], actual_json_map["wrong_line"])
	}
	if !reflect.DeepEqual(expected_json_map["answer_columns"], actual_json_map["answer_columns"]) {
		t.Errorf("expected\n%#v\nbut given\n%#v\n", expected_json_map["answer_columns"], actual_json_map["answer_columns"])
	}
	if !reflect.DeepEqual(expected_json_map["answer_records"], actual_json_map["answer_records"]) {
		t.Errorf("expected\n%#v\nbut given\n%#v\n", expected_json_map["answer_records"], actual_json_map["answer_records"])
	}
}

func TestArrangeSQL(t *testing.T) {
	var (
		sql_execute_request = SQLExecuteRequest{
			select_sql: "SELECT * from Students;",
		}
		expected_select_sql = "select * from students"
	)

	err := sql_execute_request.arrangeSQL()
	if err != nil {
		t.Errorf("expected nil but given %#v", err)
	}
	actual_select_sql := string(sql_execute_request.select_sql)
	if expected_select_sql != actual_select_sql {
		t.Errorf("expected '%s' but given '%s'", expected_select_sql, actual_select_sql)
	}
}

func TestExecuteSQL_Simple(t *testing.T) {
	var (
		// SQLExecuteRequest
		sql_execute_request = SQLExecuteRequest{
			create_sql: `create table Students (
				id int primary key,
			    name varchar(16)
			);`,
			insert_sql: `insert into Students values
				(1, 'Alice'),
				(2, 'Bob'),
				(3, 'Charlie'),
				(4, 'Dave')
			;`,
			select_sql:    "select * from Students;",
			is_explaining: false,
		}

		// SQLExecuteResult
		expected_result = SQLRows{
			{int64(1), "Alice"},
			{int64(2), "Bob"},
			{int64(3), "Charlie"},
			{int64(4), "Dave"},
		}
		actual_result      = SQLRows{}
		expected_columns   = []string{"id", "name"}
		sql_execute_result = SQLExecuteResult{
			expected_result:  &expected_result,
			actual_result:    &actual_result,
			expected_columns: &expected_columns,
			order_strict:     false,
			exec_ms:          -1,
		}
	)
	os.Setenv("SANDBOX_DB_URL", _LOCAL_DB_URL)

	err := executeSQL(&sql_execute_request, &sql_execute_result)
	if err != nil {
		t.Errorf("expected nil but given %#v", err)
	}
	if !reflect.DeepEqual(sql_execute_result.expected_result, sql_execute_result.actual_result) {
		t.Errorf("expected\n%#v\nbut given\n%#v\n", sql_execute_result.expected_result, sql_execute_result.actual_result)
	}
	if !reflect.DeepEqual(sql_execute_result.expected_columns, sql_execute_result.actual_columns) {
		t.Errorf("expected\n%#v\nbut given\n%#v\n", sql_execute_result.expected_columns, sql_execute_result.actual_columns)
	}
	if sql_execute_result.exec_ms == -1 {
		t.Errorf("expected positive value but given %#v", -1)
	}
}

func TestExecuteSQL_VariousTypes(t *testing.T) {
	var (
		// SQLExecuteRequest
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

		// SQLExecuteResult
		expected_result = SQLRows{
			{1, "A", "2019-03-01 10:00:00"},
			{2, "B", "2019-03-01 11:00:00"},
			{3, "C", "2019-03-01 12:00:00"},
			{4, "D", "2019-03-01 13:00:00"},
		}
		actual_result      = SQLRows{}
		expected_columns   = []string{"id", "c", "ts"}
		sql_execute_result = SQLExecuteResult{
			expected_result:  &expected_result,
			actual_result:    &actual_result,
			expected_columns: &expected_columns,
			order_strict:     false,
		}
	)
	os.Setenv("SANDBOX_DB_URL", _LOCAL_DB_URL)

	err := executeSQL(&sql_execute_request, &sql_execute_result)
	if err != nil {
		t.Errorf("expected nil but given %#v", err)
	}
	if !reflect.DeepEqual(sql_execute_result.expected_columns, sql_execute_result.actual_columns) {
		t.Errorf("expected\n%#v\nbut given\n%#v\n", sql_execute_result.expected_columns, sql_execute_result.actual_columns)
	}
	if sql_execute_result.exec_ms == -1 {
		t.Errorf("expected positive value but given %#v", -1)
	}
}

func TestExecuteSQL_Explain(t *testing.T) {
	var (
		// SQLExecuteRequest
		sql_execute_request = SQLExecuteRequest{
			create_sql: `create table Students (
				id int primary key,
			    name varchar(16)
			);`,
			insert_sql: `insert into Students values
				(1, 'Alice'),
				(2, 'Bob'),
				(3, 'Charlie'),
				(4, 'Dave')
			;`,
			select_sql:    "explain select * from Students;",
			is_explaining: false,
		}

		// SQLExecuteResult
		expected_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		actual_result      = SQLRows{}
		expected_columns   = []string{"QUERY PLAN"}
		sql_execute_result = SQLExecuteResult{
			expected_result:  &expected_result,
			actual_result:    &actual_result,
			expected_columns: &expected_columns,
			order_strict:     false,
			exec_ms:          -1,
		}
	)
	os.Setenv("SANDBOX_DB_URL", _LOCAL_DB_URL)

	err := executeSQL(&sql_execute_request, &sql_execute_result)
	if err != nil {
		t.Errorf("expected nil but given %#v", err)
	}
	if !reflect.DeepEqual(sql_execute_result.expected_columns, sql_execute_result.actual_columns) {
		t.Errorf("expected\n%#v\nbut given\n%#v\n", sql_execute_result.expected_columns, sql_execute_result.actual_columns)
	}
}

func TestExecuteSQL_ExplainAnalyse(t *testing.T) {
	var (
		// SQLExecuteRequest
		sql_execute_request = SQLExecuteRequest{
			create_sql: `create table Students (
				id int primary key,
			    name varchar(16)
			);`,
			insert_sql: `insert into Students values
				(1, 'Alice'),
				(2, 'Bob'),
				(3, 'Charlie'),
				(4, 'Dave')
			;`,
			select_sql:    "explain analyse select * from Students;",
			is_explaining: false,
		}

		// SQLExecuteResult
		expected_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		actual_result      = SQLRows{}
		expected_columns   = []string{"QUERY PLAN"}
		sql_execute_result = SQLExecuteResult{
			expected_result:  &expected_result,
			actual_result:    &actual_result,
			expected_columns: &expected_columns,
			order_strict:     false,
			exec_ms:          -1,
		}
	)
	os.Setenv("SANDBOX_DB_URL", _LOCAL_DB_URL)

	err := executeSQL(&sql_execute_request, &sql_execute_result)
	if err != nil {
		t.Errorf("expected nil but given %#v", err)
	}
	if !reflect.DeepEqual(sql_execute_result.expected_columns, sql_execute_result.actual_columns) {
		t.Errorf("expected\n%#v\nbut given\n%#v\n", sql_execute_result.expected_columns, sql_execute_result.actual_columns)
	}
}

func TestJudge_Match(t *testing.T) {
	var (
		// SQLExecuteResult
		expected_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		actual_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		expected_columns           = []string{"id", "name"}
		actual_columns             = []string{"id", "name"}
		matched_sql_execute_result = SQLExecuteResult{
			expected_result:  &expected_result,
			actual_result:    &actual_result,
			expected_columns: &expected_columns,
			actual_columns:   &actual_columns,
			order_strict:     false,
		}
	)

	matched_sql_execute_result.judge()
	if !matched_sql_execute_result.is_correct {
		t.Errorf("expected true but given false")
	}
}

func TestJudge_MatchStrict(t *testing.T) {
	var (
		// SQLExecuteResult
		expected_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		actual_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		expected_columns           = []string{"id", "name"}
		actual_columns             = []string{"id", "name"}
		matched_sql_execute_result = SQLExecuteResult{
			expected_result:  &expected_result,
			actual_result:    &actual_result,
			expected_columns: &expected_columns,
			actual_columns:   &actual_columns,
			order_strict:     true,
		}
	)

	matched_sql_execute_result.judge()
	if !matched_sql_execute_result.is_correct {
		t.Errorf("expected true but given false")
	}
}

func TestJudge_Unmatch(t *testing.T) {
	var (
		// SQLExecuteResult
		expected_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		actual_result = SQLRows{
			{1, "Alice"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		expected_columns             = []string{"id", "name"}
		actual_columns               = []string{"id", "name"}
		unmatched_sql_execute_result = SQLExecuteResult{
			expected_result:  &expected_result,
			actual_result:    &actual_result,
			expected_columns: &expected_columns,
			actual_columns:   &actual_columns,
			order_strict:     true,
		}

		expected_wrong_line = 2
	)

	unmatched_sql_execute_result.judge()
	if unmatched_sql_execute_result.is_correct {
		t.Errorf("expected false but given true")
	}
	if actual_wrong_line := unmatched_sql_execute_result.wrong_line; actual_wrong_line != expected_wrong_line {
		t.Errorf("expected %d but given %d", expected_wrong_line, actual_wrong_line)
	}
}

func TestJudge_UnmatchExtraRows(t *testing.T) {
	var (
		// SQLExecuteResult
		expected_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		actual_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		expected_columns             = []string{"id", "name"}
		actual_columns               = []string{"id", "name"}
		unmatched_sql_execute_result = SQLExecuteResult{
			expected_result:  &expected_result,
			actual_result:    &actual_result,
			expected_columns: &expected_columns,
			actual_columns:   &actual_columns,
			order_strict:     false,
		}

		expected_wrong_line = 4
	)

	unmatched_sql_execute_result.judge()
	if unmatched_sql_execute_result.is_correct {
		t.Errorf("expected false but given true")
	}
	if actual_wrong_line := unmatched_sql_execute_result.wrong_line; actual_wrong_line != expected_wrong_line {
		t.Errorf("expected %d but given %d", expected_wrong_line, actual_wrong_line)
	}
}

func TestJudge_UnmatchNotEnoughRows(t *testing.T) {
	var (
		// SQLExecuteResult
		expected_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		actual_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
		}
		expected_columns             = []string{"id", "name"}
		actual_columns               = []string{"id", "name"}
		unmatched_sql_execute_result = SQLExecuteResult{
			expected_result:  &expected_result,
			actual_result:    &actual_result,
			expected_columns: &expected_columns,
			actual_columns:   &actual_columns,
			order_strict:     false,
		}

		expected_wrong_line = 4
	)

	unmatched_sql_execute_result.judge()
	if unmatched_sql_execute_result.is_correct {
		t.Errorf("expected false but given true")
	}
	if actual_wrong_line := unmatched_sql_execute_result.wrong_line; actual_wrong_line != expected_wrong_line {
		t.Errorf("expected %d but given %d", expected_wrong_line, actual_wrong_line)
	}
}

func TestJudge_UnmatchStrict(t *testing.T) {
	var (
		// SQLExecuteResult
		expected_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		actual_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
		}
		expected_columns             = []string{"id", "name"}
		actual_columns               = []string{"id", "name"}
		unmatched_sql_execute_result = SQLExecuteResult{
			expected_result:  &expected_result,
			actual_result:    &actual_result,
			expected_columns: &expected_columns,
			actual_columns:   &actual_columns,
			order_strict:     true,
		}

		expected_wrong_line = 4
	)

	unmatched_sql_execute_result.judge()
	if unmatched_sql_execute_result.is_correct {
		t.Errorf("expected false but given true")
	}
	if actual_wrong_line := unmatched_sql_execute_result.wrong_line; actual_wrong_line != expected_wrong_line {
		t.Errorf("expected %d but given %d", expected_wrong_line, actual_wrong_line)
	}
}

func TestJudge_UnmatchStrictExtraRows(t *testing.T) {
	var (
		// SQLExecuteResult
		expected_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		actual_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		expected_columns             = []string{"id", "name"}
		actual_columns               = []string{"id", "name"}
		unmatched_sql_execute_result = SQLExecuteResult{
			expected_result:  &expected_result,
			actual_result:    &actual_result,
			expected_columns: &expected_columns,
			actual_columns:   &actual_columns,
			order_strict:     true,
		}

		expected_wrong_line = 4
	)

	unmatched_sql_execute_result.judge()
	if unmatched_sql_execute_result.is_correct {
		t.Errorf("expected false but given true")
	}
	if actual_wrong_line := unmatched_sql_execute_result.wrong_line; actual_wrong_line != expected_wrong_line {
		t.Errorf("expected %d but given %d", expected_wrong_line, actual_wrong_line)
	}
}

func TestJudge_UnmatchStrictNotEnoughRows(t *testing.T) {
	var (
		// SQLExecuteResult
		expected_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
			{4, "Dave"},
		}
		actual_result = SQLRows{
			{1, "Alice"},
			{2, "Bob"},
			{3, "Charlie"},
		}
		expected_columns             = []string{"id", "name"}
		actual_columns               = []string{"id", "name"}
		unmatched_sql_execute_result = SQLExecuteResult{
			expected_result:  &expected_result,
			actual_result:    &actual_result,
			expected_columns: &expected_columns,
			actual_columns:   &actual_columns,
			order_strict:     true,
		}

		expected_wrong_line = 4
	)

	unmatched_sql_execute_result.judge()
	if unmatched_sql_execute_result.is_correct {
		t.Errorf("expected false but given true")
	}
	if actual_wrong_line := unmatched_sql_execute_result.wrong_line; actual_wrong_line != expected_wrong_line {
		t.Errorf("expected %d but given %d", expected_wrong_line, actual_wrong_line)
	}
}
