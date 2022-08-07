package judge_engine

import (
	"database/sql"
	"fmt"
	"os"
	"reflect"
	"strings"
	"time"

	_ "github.com/lib/pq"
	util "github.com/ryhoh/go-util"
)

type SQL string
type SQLRows [][]interface{}
type SQLExecuteRequest struct {
	create_sql    SQL
	insert_sql    SQL
	select_sql    SQL
	is_explaining bool
}
type SQLExecuteResult struct {
	expected_result  *SQLRows
	actual_result    *SQLRows
	expected_columns *[]string
	actual_columns   *[]string
	order_strict     bool
	is_correct       bool
	wrong_line       int
	exec_ms          float64
}

const UNUSED = -1

var (
	LOCAL_DB_URL  = "postgresql://web:web@localhost:54320/sandbox?sslmode=disable"
	INHIBIT_WORDS = util.SetFromSlice(&[]string{
		"create", "update", "insert", "delete", "drop", "alter", "insert", "database", "role", "grant", "set",
		"definition", "database", "table", "current_user", "pg_user", "current_schema", "pg_roles",
	})
	ErrUseOfInhibitWords = fmt.Errorf("using inhibit words")
)

/*
	Sandbox SQL実行メイン処理

*/
func JudgeMain(
	submit_sql SQL,
	problem_name string,
) (*SQLExecuteResult, error) {
	var (
		problem             = SelectProblem(problem_name)
		sql_execute_request = SQLExecuteRequest{
			create_sql: Problem.create_sql,
			insert_sql: Problem.insert_sql,
			select_sql: submit_sql,
		}
		sql_execute_result = SQLExecuteResult{
			expected_result:  &Problem.expected_result,
			expected_columns: &Problem.expected_columns,
			order_strict:     Problem.order_strict,
		}
	)

	err := sql_execute_request.arrangeSQL()
	if err != nil {
		return &sql_execute_result, err
	}
	err = executeSQL(&sql_execute_request, &sql_execute_result)
	if err != nil {
		return &sql_execute_result, err
	}
	sql_execute_result.judge()

	return &sql_execute_result, nil
}

/*
	Return true if SQLExecuteRequest.sql_execute_request starts with "explain"
	(case insensitive)
*/
func (sql_execute_request *SQLExecuteRequest) isExplaining() bool {
	first_sentence := strings.Split(string(sql_execute_request.select_sql), ";")[0]
	first_word := strings.ToLower(strings.Split(first_sentence, " ")[0])
	sql_execute_request.is_explaining = (first_word == "explain")
	return sql_execute_request.is_explaining
}

/*
	Check and modify submitted query and return runnable sql.

    - Find illegal command
    - Extract one (first) sentence

    query: Submitted query
    return: Runnable sql
	throws: Illegal command error when INHIBIT_WORDS appear in first sentence
*/
func (sql_execute_request *SQLExecuteRequest) arrangeSQL() error {
	first_sentence := strings.ToLower(strings.Split(string(sql_execute_request.select_sql), ";")[0])
	for inhibit_word := range *INHIBIT_WORDS {
		if strings.Contains(first_sentence, inhibit_word) {
			return ErrUseOfInhibitWords
		}
	}

	sql_execute_request.select_sql = SQL(first_sentence)
	return nil
}

func extractExecMsFromQueryPlan(sql_rows *SQLRows) (float64, error) {
	for _, row := range *sql_rows {
		content := row[0]
		switch elm := content.(type) {
		case string:
			words := strings.Split(elm, " ")
			if words[0] == "Execution" {
				return float64(elm[2]), nil
			}
		default:
			continue
		}
	}

	return UNUSED, fmt.Errorf("execution time not exists in sql_rows")
}

/*
	Execute SQLExecuteRequest and store result to SQLExecuteResult

*/
func executeSQL(
	sql_execute_request *SQLExecuteRequest,
	sql_execute_result *SQLExecuteResult,
) error {
	var (
		db_address = getSandboxDBAddress()
	)

	/* Connection & Transaction Begin */
	db, err := sql.Open("postgres", db_address)
	if err != nil {
		return err
	}
	defer db.Close()

	tx, err := db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback() // Sandbox のため必ずロールバックしてきれいにしておく

	/* CREATE TABLE */
	if _, err = tx.Exec(string(sql_execute_request.create_sql)); err != nil {
		return err
	}

	/* INSERT */
	if _, err = tx.Exec(string(sql_execute_request.insert_sql)); err != nil {
		return err
	}

	/* SELECT */
	rows, err := tx.Query(string(sql_execute_request.select_sql))
	if err != nil {
		return err
	}

	/* Reseult Proccess*/
	sql_execute_result.actual_result, err = storeSQLRows(rows)
	if err != nil {
		return err
	}

	columns, err := rows.Columns()
	if err != nil {
		return nil
	}
	sql_execute_result.actual_columns = &columns

	/* Watch elapsed time */
	sql_execute_request.is_explaining = sql_execute_request.isExplaining()
	if !sql_execute_request.is_explaining {
		rows, err = tx.Query("EXPLAIN ANALYSE " + string(sql_execute_request.select_sql))
		if err != nil {
			return err
		}

		query_plan_rows, err := storeSQLRows(rows)
		if err != nil {
			return err
		}

		sql_execute_result.exec_ms, err = extractExecMsFromQueryPlan(query_plan_rows)
		if err != nil {
			return err
		}
	}

	return nil
}

/*
	Store result data from *sql.Rows into SQLRows

*/
func storeSQLRows(sql_rows *sql.Rows) (*SQLRows, error) {
	column_names, err := sql_rows.Columns()
	if err != nil {
		return nil, err
	}

	column_num := len(column_names)
	res := SQLRows{}
	for sql_rows.Next() {
		// scan to buffer
		buff := make([]interface{}, column_num)
		buff_p := make([]interface{}, column_num)
		for i := 0; i < column_num; i++ {
			buff_p[i] = &buff[i]
		}
		if err := sql_rows.Scan(buff_p...); err != nil {
			return nil, err
		}

		// convert and copy to row
		row := make([]interface{}, column_num)
		for i := 0; i < column_num; i++ {
			switch elm := buff[i].(type) {
			case int64:
				row[i] = int(elm)
			case float64:
				row[i] = float64(elm)
			case []uint8:
				row[i] = string(elm)
			case string:
				row[i] = string(elm)
			case rune:
				row[i] = rune(elm)
			case time.Time:
				row[i] = elm.Format("2006-01-02 15:04:05")
			default:
				return nil, fmt.Errorf("unsupported data type: %T", elm)
			}
		}
		res = append(res, row)
	}

	return &res, nil
}

// Returns Sandbox DB address
func getSandboxDBAddress() string {
	env, env_exists := os.LookupEnv("SANDBOX_DB_URL")
	if !env_exists {
		return LOCAL_DB_URL
	}
	return env
}

/*
	クエリ結果が模範解答と等しいかを比べる

    expected SQLRows 模範解答
    answered SQLRows 提出解答
    order_strict bool ORDER BY などで順序一致を求めるか
    return (正解したか, 不正解の場合 answered の最初の不一致行)
*/

/*
	実行結果答え合わせ

	sql_execute_result *SQLExecuteResult SQL実行結果
	(正解したか, 不正解の場合 answered の最初の不一致行) -> sql_execute_result.is_correct, sql_execute_result.wrong_line
*/
func (sql_execute_result *SQLExecuteResult) judge() {
	var (
		expected     = *sql_execute_result.actual_result
		answered     = *sql_execute_result.actual_result
		order_strict = sql_execute_result.order_strict
		p_is_correct = &sql_execute_result.is_correct
		p_wrong_line = &sql_execute_result.wrong_line
	)

	if order_strict { // 順序まで要求する場合
		if reflect.DeepEqual(expected, answered) { // 完全一致
			*p_is_correct, *p_wrong_line = true, UNUSED
			return
		}
		var i int = 0
		for ; i < util.Min(len(expected), len(answered)); i++ {
			expected_record := (expected)[i]
			answered_record := (answered)[i]
			if !reflect.DeepEqual(expected_record, answered_record) {
				*p_is_correct, *p_wrong_line = false, i+1 // 最初に不一致した行の番号を返す
				return
			}
		}
		*p_is_correct, *p_wrong_line = false, i+1 // answered が途中まで正しいが、レコードが途中で終わった場合など
		return
	}

	// 順序まで要求しない場合
	checked := make([]bool, len(expected))
	idx := 0
	for i, answered_record := range answered { // answer を1行ずつチェック
		idx = i + 1
		for j, expected_record := range expected {
			if !checked[j] && reflect.DeepEqual(answered_record, expected_record) { // 未チェックかつ一致
				checked[j] = true
				continue
			}
			*p_is_correct, *p_wrong_line = false, i+1 // expected のどの行にも一致しなかった
			return
		}
	}
	// この時点で answered ⊆ expected
	// for i := 0; i < len(checked); i++ {
	// 	if !checked[i] { // answered の行数が不足 answered ⊂ expected
	// 		return false, idx + 1
	// 	}
	// }
	if !util.All(checked...) {
		*p_is_correct, *p_wrong_line = false, idx // answered の行数が不足 answered ⊂ expected
		return
	}
	*p_is_correct, *p_wrong_line = true, UNUSED // answered = expected
}
