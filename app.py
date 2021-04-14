import glob
import json
from typing import Dict, Any

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import psycopg2
import uvicorn

import sandbox_db
import judge

app = FastAPI()
app.mount("/api/problems", StaticFiles(directory="problems"), name="problems")
app.mount("/static", StaticFiles(directory="static"), name="static")

explanation = "Let's practice SQL on this service!"
problems_list = frozenset(
    name.removeprefix('problems/').removesuffix('.json')
    for name in glob.glob('problems/*.json', recursive=False)
)


@app.get('/')
async def root(request: Request):
    await request.send_push_promise('static/style_template.css')
    await request.send_push_promise('static/style.css')
    await request.send_push_promise('static/main.js')
    return FileResponse('static/index.html')


@app.get('/api/v1/help')
async def get_help():
    return {
        'help': explanation,
    }


@app.get('/api/v1/problem')
def get_problem(problem_name: str):
    return load_problem(problem_name)


@app.get('/api/v1/problem_list')
async def get_problem_list():
    return {
        'problems': problems_list
    }


@app.post('/api/v1/submit')
def submit_answer(problem_name: str = Form(...), answer: str = Form(...)):
    problem: Dict[str, Any] = load_problem(problem_name)
    result: sandbox_db.Result = sandbox_db.execute(ddl=problem["DDL"], tables=problem["tables"], query=answer)

    if result.has_error:
        return {
            "result": "PE",
            "message": result.error_message
        }

    expected = problem['expected']
    correct, wrong_line = judge.judge(
        expected=[tuple(record) for record in expected["records"]],
        answered=result.records,
        order_strict=expected["order_sensitive"]
    )

    return {
        "result": "AC" if correct else "WA",
        "wrong_line": wrong_line,
        "answer_columns": result.columns,
        "answer_records": result.records,
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


if __name__ == '__main__':
    uvicorn.run(app)
