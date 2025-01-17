from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database import database
from security import (
    create_jwt_token,
    decode_jwt_token,
    hash_password, 
    verify_password,
)


app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def get_dashboard(request: Request):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse("/signin", status_code=302)

    try:
        token = decode_jwt_token(token)
    except:
        return RedirectResponse("/signin", status_code=302)
    
    user = await database.select("users", ["username"], f"id = {token['user_id']}", single=True)

    return templates.TemplateResponse("/dashboard/dashboard.html", {"request": request, "user": user})


@app.get("/signup")
async def get_signup(request: Request):
    return templates.TemplateResponse("/auth/signup.html", {"request": request})


@app.post("/signup")
async def post_signup(request: Request):
    form = await request.form()
    
    username = form.get("username")
    email = form.get("email")
    password = form.get("password")
    repeat_password = form.get("repeat_password")

    # TODO: Add validation for username, email, password, and repeat_password
    user = await database.select("users", ["*"], f"email = '{email}'")
    if user:
        return RedirectResponse("/signin", status_code=302)

    password = hash_password(password)

    await database.insert("users", ["username", "email", "password"], [username, email, password])
    return templates.TemplateResponse("/auth/signin.html", {"request": request})


@app.get("/signin")
async def get_signin(request: Request):
    return templates.TemplateResponse("/auth/signin.html", {"request": request})


@app.post("/signin")
async def post_signin(request: Request):
    form = await request.form()

    email = form.get("email")
    password = form.get("password")

    user = await database.select("users", ["password", "id"], f"email = '{email}'", single=True)

    if user and verify_password(password, user[0]):
        token = create_jwt_token({"user_id": user[1]})
        response = RedirectResponse("/", status_code=302)
        response.set_cookie("token", token)
        return response
    else:
        return RedirectResponse("/signin", status_code=302)


@app.post("/logout")
async def post_signout(request: Request):
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("token")
    return response


@app.get("/urls/new")
async def get_new_url(request: Request):
    return templates.TemplateResponse("/urls/create.html", {"request": request})
