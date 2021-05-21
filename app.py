from datetime import timedelta
import glob
import json
from typing import Any, Dict, List

from fastapi import Body, Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import natsort
import uvicorn

import authorization
import db
import judge
import sandbox_db


app = FastAPI()
app.mount("/api/problems", StaticFiles(directory="problems"), name="problems")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

problems_list: List[str] = natsort.natsorted(
    name.removeprefix('problems/').removesuffix('.json')
    for name in glob.glob('problems/*.json', recursive=False)
)
problems_num = len(problems_list)
sandbox_psql_version = ' '.join(sandbox_db.read_version().split()[:2])  # 'PostgreSQL XX.X'


# End points
@app.get('/')
async def root(request: Request):
    await request.send_push_promise('static/style_template.css')
    await request.send_push_promise('static/style.css')
    await request.send_push_promise('static/main.js')
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "psql_version": sandbox_psql_version,
        }
    )


@app.get('/api/v1/problem')
def get_problem(problem_name: str):
    return load_problem(problem_name)


@app.get('/api/v1/problem_list')
async def get_problem_list():
    return {'problems': problems_list}


@app.get('/api/v1/info')
def get_info():
    return {'version': sandbox_psql_version}


@app.post('/api/v1/token')
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authorization.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=authorization.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = authorization.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    cleared_problems = set(
        elms[0] for elms in
        db.read_cleared_problem_from_result(user.username)
    )
    cleared_flags = [problem in cleared_problems for problem in problems_list]

    return {
        "access_token": access_token,
        "token_type": "bearer",
        'cleared_num': sum(cleared_flags),
        'cleared_flags': cleared_flags,
    }


@app.post('/api/v1/signup')
def signup(name: str = Form(...), password: str = Form(...)):
    if name == '' or len(name) < 4 or 30 < len(name) or not name.isalnum():
        return {'result': 'name_invalid'}

    if password == '' or len(password) < 8 or 60 < len(password) or not password.isascii():
        return {'result': 'password_invalid'}

    success = db.create_user(name=name, password=authorization.get_password_hash(password).encode())
    if not success:
        return {'result': 'failed'}

    access_token_expires = timedelta(minutes=authorization.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = authorization.create_access_token(
        data={"sub": name}, expires_delta=access_token_expires
    )

    return {
        'result': 'success',
        "access_token": access_token,
        "token_type": "bearer",
        'cleared_num': 0,
        'cleared_flags': [False for _ in range(problems_num)]
    }


@app.post('/api/v1/test')
def test_answer(problem_name: str = Form(...), answer: str = Form(...),):
    return execute_answer(problem_name, answer)


@app.post('/api/v1/submit')
def submit_answer(
        problem_name: str = Body(...),
        answer: str = Body(...),
        user: authorization.UserInDB = Depends(authorization.get_current_user)
):
    ret_val = execute_answer(problem_name, answer)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update record
    db.create_problem(problem_name)
    db.upsert_result(problem_name, user.username, ret_val['result'])
    cleared_problems = set(
        elms[0] for elms in
        db.read_cleared_problem_from_result(user.username)
    )
    cleared_flags = [problem in cleared_problems for problem in problems_list]
    ret_val["cleared_num"] = sum(cleared_flags)
    ret_val['cleared_flags'] = cleared_flags

    return ret_val


# Functions
def check_problem_name(problem_name: str):
    if ".." in problem_name:  # 関係ないディレクトリにアクセスさせない
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    elif problem_name not in problems_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")


def execute_answer(problem_name: str, answer: str) -> Dict[str, Any]:
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

    return {
        "result": "AC" if correct else "WA",
        "wrong_line": wrong_line,
        "answer_columns": result.columns,
        "answer_records": result.records,
    }


def load_problem(problem_name: str) -> Dict[str, Any]:
    check_problem_name(problem_name)
    try:
        with open("problems/" + problem_name + ".json", "r") as f:
            problem = json.load(f)
    except IOError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Problem load failed"
        )
    return problem


if __name__ == '__main__':
    uvicorn.run(app)
