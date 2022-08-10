package storage

import (
	"encoding/json"
	"io/ioutil"
	"sort"
	"strings"

	"github.com/maruel/natural"

	. "sqlpuzzlers/internal/common"
)

var (
	_DB_TYPES_TO_GO_TYPES = map[string]string{
		"int":      "int64",
		"integer":  "int64",
		"float":    "float64",
		"double":   "float64",
		"varchar":  "string",
		"char":     "string",
		"nvarchar": "string",
		"nchar":    "string",
	}
	PROBLEM_DIR = "web/static/problems"
)

// raw (on json) data
type ProblemJson struct {
	Descriptions struct {
		EN []string
		JP []string
	}
	Create_sql []string
	Insert_sql []string
	Expected   struct {
		Expected_columns []string
		Expected_types   []string
		Expected_result  [][]interface{}
		Order_strict     bool
	}
	Writers []string
}

// ready to display data
type descriptions_t struct {
	EN string
	JP string
}
type expected_t struct {
	Expected_columns []string
	Expected_types   []string
	Expected_result  SQLRows
	Order_strict     bool
}
type Problem struct {
	Descriptions descriptions_t
	Create_sql   SQL
	Insert_sql   SQL
	Expected     expected_t
	Writers      string
}

func SelectProblem(problem_name string) (*Problem, error) {
	/* Read from file */
	json_bytes, err := ioutil.ReadFile(problem_name)
	if err != nil {
		return nil, err
	}

	/* Load from json */
	var problem_json ProblemJson
	json.Unmarshal(json_bytes, &problem_json)

	/* Conversion */
	if err := problem_json.result_type_conversion(); err != nil {
		return nil, err
	}

	/* Copy and conversion */
	var problem Problem
	problem.Descriptions.EN = strings.Join(problem_json.Descriptions.EN, "\n")
	if problem_json.Descriptions.JP != nil {
		problem.Descriptions.JP = strings.Join(problem_json.Descriptions.JP, "\n")
	}
	problem.Create_sql = SQL(strings.Join(problem_json.Create_sql, ""))
	problem.Insert_sql = SQL(strings.Join(problem_json.Insert_sql, ""))
	problem.Expected.Expected_columns = problem_json.Expected.Expected_columns
	problem.Expected.Expected_types = make([]string, 0)
	for i := 0; i < len(problem_json.Expected.Expected_types); i++ {
		problem.Expected.Expected_types = append(problem.Expected.Expected_types, strings.ToLower(problem_json.Expected.Expected_types[i]))
	}
	problem.Expected.Expected_result = problem_json.Expected.Expected_result
	problem.Expected.Order_strict = problem_json.Expected.Order_strict
	problem.Writers = joinWriters(problem_json.Writers)

	return &problem, nil
}

func (problem_json *ProblemJson) result_type_conversion() error {
	row_num := len(problem_json.Expected.Expected_result)
	column_num := len(problem_json.Expected.Expected_columns)

	for i := 0; i < row_num; i++ {
		for j := 0; j < column_num; j++ {
			target := &problem_json.Expected.Expected_result[i][j]
			target_type := _DB_TYPES_TO_GO_TYPES[problem_json.Expected.Expected_types[j]]
			SQLResultTypeConversion(target, target)
			if target_type == "int64" { // re-convert from float64 to int64
				switch elm := (*target).(type) {
				case float64:
					*target = int64(elm)
				}
			}
		}
	}

	return nil
}

func joinWriters(writers []string) string {
	length := len(writers)
	switch length {
	case 0:
		return ""
	case 1:
		return writers[0]
	default:
		res := ""
		for i := 0; i < length-2; i++ {
			res += writers[i] + ", "
		}
		res += writers[length-2] + " and " + writers[length-1]
		return res
	}
}

func GetProblemList() ([]string, error) {
	problem_list := []string{}
	files, err := ioutil.ReadDir(PROBLEM_DIR)
	if err != nil {
		return nil, err
	}

	for _, file := range files {
		file_name := file.Name()
		file_name_parts := strings.Split(file_name, ".")
		if file_name_parts[1] == "json" {
			problem_list = append(problem_list, file_name_parts[0])
		}
	}

	sort.Sort(natural.StringSlice(problem_list))
	return problem_list, nil
}
