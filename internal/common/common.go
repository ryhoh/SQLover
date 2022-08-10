package common

import (
	"fmt"
	"strings"
	"time"

	"github.com/ryhoh/go-util"
)

type SQL string
type SQLRows [][]interface{}

const UNUSED = -1

func SQLResultTypeConversion(from, to *interface{}) error {
	switch elm := (*from).(type) {
	case int64:
		*to = int64(elm)
	case float64:
		*to = float64(elm)
	case []uint8:
		*to = string(elm)
	case string:
		*to = string(elm)
	case rune:
		*to = rune(elm)
	case time.Time:
		*to = elm.Format("2006-01-02 15:04:05")
	default:
		return fmt.Errorf("unsupported data type: %T", elm)
	}

	return nil
}

func ProblemTypeExtraction(problem_names []string) []string {
	problem_types := util.Set[string]{}
	for _, problem_name := range problem_names {
		problem_types.Add(strings.Split(problem_name, "-")[0])
	}

	res := []string{}
	for problem_type := range problem_types {
		res = append(res, problem_type)
	}

	return res
}
