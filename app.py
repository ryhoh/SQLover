import glob
import json
import sqlite3
from typing import Iterable

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

import db
import judge

app = FastAPI()
app.mount("/api/problems", StaticFiles(directory="problems"), name="problems")
app.mount("/static", StaticFiles(directory="static"), name="static")

explanation = 'Let\'s practice SQL on this service!'


@app.get('/')
async def root():
    return FileResponse('static/index.html')


@app.get('/api/v1/help')
async def get_help():
    return {
        'help': explanation,
    }


@app.get('/api/v1/problem')
def get_problem(problem_name: str):
    problem = load_problem(problem_name)

    # JavaScript で読める形で正答の表を渡す
    problem['expected_records'] = eval(problem["expected_expr"])
    return problem


@app.get('/api/v1/problem_list')
def get_problem_list():
    return {
        'problems': problems_list()
    }


@app.post('/api/v1/submit')
def submit_answer(problem_name: str = Form(...), answer: str = Form(...)):
    problem = load_problem(problem_name)
    try:
        result = db.execute(ddl=problem["DDL"], tables=problem["tables"], query=answer)
    except sqlite3.OperationalError as e:
        return {
            "Result": "RE",
            "Message": str(e)
        }
    correct, wrong_line = judge.judge(
        expected=eval(problem["expected_expr"]), answered=result, order_strict=problem["order_strict"])

    return {
        "Result": "AC" if correct else "WA",
        "Wrong Line": wrong_line,
    }


def check_problem_name(problem_name: str):
    if ".." in problem_name:  # 関係ないディレクトリにアクセスさせない
        raise HTTPException(status_code=403, detail="Forbidden")


def load_problem(problem_name: str) -> dict:
    check_problem_name(problem_name)
    try:
        with open("problems/" + problem_name + ".json", "r") as f:
            problem = json.load(f)
    except IOError:
        raise HTTPException(status_code=503, detail="Problem load failed")
    return problem


def problems_list() -> Iterable[str]:
    problems = glob.glob('problems/*.json', recursive=False)
    return (name.removeprefix('problems/').removesuffix('.json')
            for name in problems)


if __name__ == '__main__':
    uvicorn.run(app)
