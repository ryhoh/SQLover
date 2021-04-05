import json
import sqlite3

import uvicorn
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import db
import judge

app = FastAPI()
app.mount("/api/problems", StaticFiles(directory="problems"), name="problems")

explanation = 'SQL を練習できるサービスです。'


@app.get('/')
async def root():
    return {
        'help': explanation,
    }


@app.get('/api/problems')
def get_problem(problem_name: str):
    check_problem_name(problem_name)
    return FileResponse('problems/' + problem_name + '.json')


@app.post('/api/submit')
def submit_problem(problem_name: str = Form(...), answer: str = Form(...)):
    check_problem_name(problem_name)
    try:
        with open("problems/" + problem_name + ".json", "r") as f:
            problem = json.load(f)
    except IOError:
        raise HTTPException(status_code=503, detail="Problem load failed")

    try:
        result = db.execute(ddl=problem["DDL"], query=answer)
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


if __name__ == '__main__':
    uvicorn.run(app)
