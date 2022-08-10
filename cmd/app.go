package main

import (
	"encoding/json"
	"html/template"
	"net/http"

	"sqlpuzzlers/internal/common"
	"sqlpuzzlers/internal/judge"
	"sqlpuzzlers/internal/storage"
)

/* / */
func root(response_writer http.ResponseWriter, request *http.Request) {
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

func main() {
	http.HandleFunc("/", root)
	http.HandleFunc("/api/v1/problem_list", problem_list)

	fileServer := http.FileServer(http.Dir("web/static"))
	http.Handle("/static/", http.StripPrefix("/static/", fileServer))

	http.ListenAndServe(":8080", nil)
}
