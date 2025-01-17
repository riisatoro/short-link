import os

from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND

from database import database
from dependencies import get_request_user
from security import (
    create_jwt_token,
    decode_jwt_token,
    hash_password, 
    verify_password,
)
from url_shortener import make_short_url


DOMAIN = "http://localhost:8000"


app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def get_dashboard(
    request: Request,
    user = Depends(get_request_user),
):
    urls = await database.select(
        "urls", 
        ["id", "full_url", "short_url", "count_visits", "visits"], 
        f"user_id = {user[0]}"
    )
    return templates.TemplateResponse("/dashboard/dashboard.html", {"request": request, "user": user, "urls": urls})


@app.get("/{url_key}")
async def redirect_to_full_url(request: Request, url_key: str):
    short_url = os.path.join(DOMAIN, url_key)
    url = await database.select("urls", ["full_url", "visits", "single_use", "count_visits"], f"short_url = '{short_url}'", single=True)
    if url[3]:
        await database.update("urls", ["visits"], [url[1] + 1], f"short_url = '{url_key}'")
        return RedirectResponse(url[0], status_code=HTTP_302_FOUND)
    elif url[2]:
        await database.delete("urls", f"short_url = '{short_url}'")
        return RedirectResponse(url[0], status_code=HTTP_302_FOUND)
    else:
        return RedirectResponse("/", status_code=HTTP_302_FOUND)


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
        return RedirectResponse("/signin", status_code=HTTP_302_FOUND)

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
        response = RedirectResponse("/", status_code=HTTP_302_FOUND)
        response.set_cookie("token", token)
        return response
    else:
        return RedirectResponse("/signin", status_code=HTTP_302_FOUND)


@app.post("/logout")
async def post_signout(request: Request):
    response = RedirectResponse("/", status_code=HTTP_302_FOUND)
    response.delete_cookie("token")
    return response


@app.get("/urls/new")
async def get_new_url(request: Request, user = Depends(get_request_user)):
    return templates.TemplateResponse("/urls/create.html", {"request": request})


@app.post("/urls/new")
async def post_new_url(request: Request, user = Depends(get_request_user)):
    form = await request.form()
    url = form.get("url")
    single_use = form.get("single_use")
    count_visits = form.get("count_usage")

    short_url = os.path.join(DOMAIN, make_short_url())
    await database.insert(
        "urls",
        ["user_id", "full_url", "short_url", "single_use", "count_visits"],
        [user[0], url, short_url, single_use, count_visits]
    )

    return RedirectResponse("/", status_code=HTTP_302_FOUND)


@app.post("/urls/{url_id}/delete")
async def get_delete_url(request: Request, url_id: int, user = Depends(get_request_user)):
    url_to_delete = await database.select("urls", ["id", "full_url"], f"id = {url_id}", single=True)
    if not url_to_delete:
        return RedirectResponse("/", status_code=HTTP_302_FOUND)
    
    await database.delete("urls", f"id = {url_id}")
    return RedirectResponse("/", status_code=HTTP_302_FOUND)
