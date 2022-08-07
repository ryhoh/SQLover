package main

import (
	"fmt"
	"net/http"
)

func hello(response_writer http.ResponseWriter, request *http.Request) {
	fmt.Fprintf(response_writer, "Hello!")
}

func main() {
	http.HandleFunc("/", hello)
	http.ListenAndServe(":8080", nil)
}
