package common

import (
	"fmt"
	"time"
)

type SQL string
type SQLRows [][]interface{}

const UNUSED = -1

func SQLResultTypeConversion(from, to *interface{}) error {
	switch elm := (*from).(type) {
	case int64:
		*to = int(elm)
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
