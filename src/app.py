from datetime import timedelta
import glob
import json
import sys
from typing import Any, Dict, List, Union

from fastapi import Body, Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import natsort
import uvicorn

from src import authorization, db, sandbox_db, judge
from src.mail_session import ResetPasswordMailSession, SignupMailSession


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
    await request.send_push_promise('../static/style_template.css')
    await request.send_push_promise('../static/style.css')
    await request.send_push_promise('../static/main.js')
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "psql_version": sandbox_psql_version,
        }
    )


@app.get('/activate')
async def activate_account(param: str):
    ms_id = param
    try:
        user_signup_session = SignupMailSession.sessions[ms_id]
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    if user_signup_session.is_expired():
        SignupMailSession.sessions.pop(ms_id)
        return PlainTextResponse('Session expired. Try signup procedure again.\n\
時間切れです。もう一度、登録手続きをしてください。')

    db.update_users_active(user_signup_session.user_name)
    SignupMailSession.sessions.pop(ms_id)
    return PlainTextResponse('Signup successfully done! Please close window and login.\n\
登録に成功しました！ウィンドウを閉じて、ログインしてください。')


@app.get('/forgot_password/{language}')
async def forgot_password(request: Request, language: str):
    if 'en' == language:
        return templates.TemplateResponse("forgot_password.html", {"request": request})
    if 'ja' == language:
        return templates.TemplateResponse("forgot_password_ja.html", {"request": request})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")


@app.get('/reset_password')
async def reset_password(request: Request, param: str):
    ms_id = param
    try:
        user_reset_password_session = ResetPasswordMailSession.sessions[ms_id]
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    if user_reset_password_session.is_expired():
        ResetPasswordMailSession.sessions.pop(ms_id)
        return PlainTextResponse('Session expired. Try signup procedure again.\n\
時間切れです。もう一度、登録手続きをしてください。')
    return templates.TemplateResponse("reset_password.html", {"request": request, "ms_id": ms_id})


@app.post('/request_reset_password')
async def request_reset_password(email: str = Form(...), language: str = Form(...)):
    if email == '' or email.count('@') != 1:
        return {'result': 'invalid_email'}

    try:
        username = db.read_username_from_user_by_email(email)
    except ValueError:
        return PlainTextResponse('The email is not registered.\n\
登録されていないメールアドレスです。')

    ResetPasswordMailSession(username).send_mail(language, email)
    return PlainTextResponse('Verification mail has send. Please check it out.\n\
認証用メールが送信されました。確認してください。')


@app.get('/signup/{language}')
async def signup_page(request: Request, language: str):
    if 'en' == language:
        return templates.TemplateResponse("signup.html", {"request": request})
    if 'ja' == language:
        return templates.TemplateResponse("signup_ja.html", {"request": request})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")


@app.post('/update_password')
async def update_password(
        password: str = Form(...),
        password_confirm: str = Form(...),
        ms_id: str = Form(...)
):
    if password == '' or len(password) < 8 or 60 < len(password) or not password.isascii():
        return {'result': 'invalid_password'}
    if password != password_confirm:
        return {'result': 'Passwords are not same.'}

    try:
        user_reset_password_session = ResetPasswordMailSession.sessions[ms_id]
    except KeyError:
        sys.stderr.write('%s is not in %s\n' % (ms_id, ResetPasswordMailSession.sessions))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    if user_reset_password_session.is_expired():
        ResetPasswordMailSession.sessions.pop(ms_id)
        return PlainTextResponse('Session expired. Try signup procedure again.\n\
時間切れです。もう一度、登録手続きをしてください。')

    db.update_users_password(
        user_reset_password_session.user_name,
        authorization.get_password_hash(password).encode()
    )
    ResetPasswordMailSession.sessions.pop(ms_id)
    return PlainTextResponse('Password reset successfully done! Please close window and login.\n\
パスワードの変更に成功しました！ウィンドウを閉じて、ログインしてください。')


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
    user: Union[authorization.UserInDB, bool] = authorization.authenticate_user(form_data.username, form_data.password)
    if not user or not user.is_active:
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
def signup(
        email: str = Form(...),
        username: str = Form(...),
        password: str = Form(...),
        password_confirm: str = Form(...),
        language: str = Form(...)
):
    if email == '' or email.count('@') != 1:
        return {'result': 'invalid_email'}
    if username == '' or len(username) < 4 or 30 < len(username) or not username.isalnum():
        return {'result': 'invalid_username'}
    if password == '' or len(password) < 8 or 60 < len(password) or not password.isascii():
        return {'result': 'invalid_password'}
    if password != password_confirm:
        return {'result': 'Passwords are not same.'}

    success = db.create_user(username, authorization.get_password_hash(password).encode(), email)
    if not success:
        return PlainTextResponse('This username or email address is already used.\n\
このユーザ名またはメールアドレスはすでに使われています。')

    SignupMailSession(username).send_mail(language, email)
    return PlainTextResponse('Verification mail has send. Please check it out.\n\
認証用メールが送信されました。確認してください。')


@app.post('/api/v1/test')
def test_answer(problem_name: str = Form(...), answer: str = Form(...)):
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
        "exec_ms": result.exec_ms,
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
