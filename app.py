import glob
import json
from typing import Dict, Any, List

import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import natsort
from passlib.context import CryptContext

import db
import judge
import sandbox_db

SECRET_KEY = 'd6db23525330c4807115b31ddf9efeb707dc3c29ae139dde'


app = FastAPI()
app.mount("/api/problems", StaticFiles(directory="problems"), name="problems")
app.mount("/static", StaticFiles(directory="static"), name="static")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

explanation = "Let's practice SQL on this service!"
problems_list: List[str] = natsort.natsorted(
    name.removeprefix('problems/').removesuffix('.json')
    for name in glob.glob('problems/*.json', recursive=False)
)
problems_num = len(problems_list)


# End points
@app.get('/')
async def root(request: Request):
    await request.send_push_promise('static/style_template.css')
    await request.send_push_promise('static/style.css')
    await request.send_push_promise('static/main.js')
    return FileResponse('static/index.html')


@app.get('/api/v1/help')
async def get_help():
    return {'help': explanation}


@app.get('/api/v1/problem')
def get_problem(problem_name: str):
    return load_problem(problem_name)


@app.get('/api/v1/problem_list')
async def get_problem_list():
    return {'problems': problems_list}


@app.post('/api/v1/login')
def login(name: str = Form(...), password: str = Form(...)):
    try:
        hashed_passwd = db.read_passwd_by_name_from_user(name)
    except ValueError:
        return {'result': 'failed'}

    accepted = verify_password(password, hashed_passwd)
    cleared_problems = set(
        elms[0] for elms in
        db.read_cleared_problem_from_result(name)
    )
    cleared_flags = [problem in cleared_problems for problem in problems_list]
    return {
        'result': 'success' if accepted else 'failed',
        'cleared_num': sum(cleared_flags),
        'cleared_flags': cleared_flags,
    }


@app.post('/api/v1/signup')
def signup(name: str = Form(...), password: str = Form(...)):
    if name == '' or len(name) < 4 or 30 < len(name) or not name.isalnum():
        return {'result': 'name_invalid'}

    if password == '' or len(password) < 8 or 60 < len(password) or not password.isascii():
        return {'result': 'password_invalid'}

    success = db.create_user(name=name, password=get_password_hash(password))
    return {
        'result': 'success' if success else 'failed',
        'cleared_num': 0,
        'cleared_flags': [False for _ in range(problems_num)]
    }


@app.post('/api/v1/submit')
def submit_answer(
        problem_name: str = Form(...),
        answer: str = Form(...),
        user_name: str = Form(None),
        user_passwd: str = Form(None)
):
    # run SQL
    problem: Dict[str, Any] = load_problem(problem_name)
    result: sandbox_db.Result = sandbox_db.execute(ddl=problem["DDL"], tables=problem["tables"], query=answer)

    if result.has_error:
        return {
            "result": "PE",
            "message": result.error_message
        }

    # Judge
    expected = problem['expected']
    correct, wrong_line = judge.judge(
        expected=[tuple(record) for record in expected["records"]],
        answered=result.records,
        order_strict=expected["order_sensitive"]
    )

    ret_val = {
        "result": "AC" if correct else "WA",
        "wrong_line": wrong_line,
        "answer_columns": result.columns,
        "answer_records": result.records,
    }

    # Update record
    if user_name and user_passwd:
        db.create_problem(problem_name)
        db.upsert_result(problem_name, user_name, "AC" if correct else "WA")
        cleared_problems = set(
            elms[0] for elms in
            db.read_cleared_problem_from_result(user_name)
        )
        cleared_flags = [problem in cleared_problems for problem in problems_list]
        ret_val["cleared_num"] = sum(cleared_flags)
        ret_val['cleared_flags'] = cleared_flags

    return ret_val


# Functions
def check_problem_name(problem_name: str):
    if ".." in problem_name:  # 関係ないディレクトリにアクセスさせない
        raise HTTPException(status_code=403, detail="Forbidden")
    elif problem_name not in problems_list:
        raise HTTPException(status_code=404, detail="Not Found")


def get_password_hash(password: str) -> bytes:
    return pwd_context.hash(password)


def load_problem(problem_name: str) -> Dict[str, Any]:
    check_problem_name(problem_name)
    try:
        with open("problems/" + problem_name + ".json", "r") as f:
            problem = json.load(f)
    except IOError:
        raise HTTPException(status_code=503, detail="Problem load failed")
    return problem


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


if __name__ == '__main__':
    uvicorn.run(app)
