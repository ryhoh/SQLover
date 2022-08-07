package storage

import (
	"reflect"
	"testing"

	. "sqlovers/internal/common"
)

func TestSelectProblem(t *testing.T) {
	expected := Problem{
		Descriptions: descriptions_t{
			EN: "This is the first problem.\nJust select all.",
			JP: "最初の問題です。\n表全体をそのまま出力してください。",
		},
		Create_sql: "create table Students (       id int primary key,       name varchar(16));",
		Insert_sql: "insert into Students values       (1, 'Alice'),       (2, 'Bob'),       (3, 'Charlie'),       (4, 'Dave'));",
		Expected: expected_t{
			Expected_columns: []string{"id", "name"},
			Expected_types:   []string{"int", "varchar"},
			Expected_result: SQLRows{
				{int64(1), "Alice"},
				{int64(2), "Bob"},
				{int64(3), "Charlie"},
				{int64(4), "David"},
			},
			Order_strict: false,
		},
		Writers: "ryhoh",
	}

	actual, err := SelectProblem("../../problems/sample-1.json")
	if err != nil {
		t.Errorf("expected nil but given %#v", err)
	}

	if !reflect.DeepEqual(expected, *actual) {
		t.Errorf("expected \n%#v\n but given \n%#v\n", expected, *actual)
	}
}
