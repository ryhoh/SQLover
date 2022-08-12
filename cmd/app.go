package main

import (
	"encoding/json"
	"fmt"
	"html/template"
	"net/http"
	"os"

	"sqlpuzzlers/internal/common"
	"sqlpuzzlers/internal/judge"
	"sqlpuzzlers/internal/storage"
)

/* /index */
func index(response_writer http.ResponseWriter, request *http.Request) {
	psql_version, err := judge.ReadVersion()
	if err != nil {
		http.Error(response_writer, err.Error(), http.StatusInternalServerError)
		return
	}

	tp := template.Must(template.ParseFiles("web/template/index.html"))
	err = tp.Execute(
		response_writer,
		map[string]interface{}{
			"psql_version": psql_version,
		},
	)
	if err != nil {
		http.Error(response_writer, err.Error(), http.StatusInternalServerError)
		return
	}
}

/* /api/v1/problem_list */
func problem_list(response_writer http.ResponseWriter, request *http.Request) {
	type ProblemList struct {
		Problems      []string `json:"problems"`
		Problem_types []string `json:"problem_types"`
	}

	problems, err := storage.GetProblemList()
	if err != nil {
		http.Error(response_writer, err.Error(), http.StatusInternalServerError)
		return
	}

	problem_list := ProblemList{
		Problems:      problems,
		Problem_types: common.ProblemTypeExtraction(problems),
	}

	res, err := json.Marshal(problem_list)
	if err != nil {
		http.Error(response_writer, err.Error(), http.StatusInternalServerError)
		return
	}

	response_writer.Header().Set("Content-Type", "application/json")
	response_writer.Write(res)
}

/* /api/v1/test */
func test(response_writer http.ResponseWriter, request *http.Request) {
	err := request.ParseForm()
	if err != nil {
		http.Error(response_writer, err.Error(), http.StatusInternalServerError)
		return
	}

	problem_name := request.Form.Get("problem_name")
	answer := request.Form.Get("answer")
	if problem_name == "" || answer == "" {
		http.Error(response_writer, fmt.Sprintf("bad parameter problem_name: %s, answer: %s", problem_name, answer), http.StatusBadRequest)
		return
	}

	json_map, err := judge.JudgeMain(common.SQL(answer), problem_name)
	if err != nil && json_map == nil { // server-side error
		http.Error(response_writer, err.Error(), http.StatusInternalServerError)
		return
	}
	/* (err != nil && json_map != nil) -> user's programming error */

	json_bytes, err := json.Marshal(*json_map)
	if err != nil {
		http.Error(response_writer, err.Error(), http.StatusInternalServerError)
		return
	}
	response_writer.Header().Set("Content-Type", "application/json")
	response_writer.Write(json_bytes)
}

func main() {
	http.HandleFunc("/index", index)
	http.HandleFunc("/api/v1/problem_list", problem_list)
	http.HandleFunc("/api/v1/test", test)

	fileServer := http.FileServer(http.Dir("web/static"))
	http.Handle("/static/", http.StripPrefix("/static/", fileServer))

	// http.ListenAndServe(":8080", nil)
	http.ListenAndServe(":"+os.Getenv("PORT"), nil)
}
