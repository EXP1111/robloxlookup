from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()

app.mount("/static", StaticFiles(directory="."), name="static")
templates = Jinja2Templates(directory=".")

ROBLOX_USERS_API = "https://users.roblox.com/v1"
ROBLOX_FRIENDS_API = "https://friends.roblox.com/v1"
ROBLOX_PRESENCE_API = "https://presence.roblox.com/v1"
ROBLOX_GROUPS_API = "https://groups.roblox.com/v1"
ROBLOX_BADGES_API = "https://badges.roblox.com/v1"
ROBLOX_THUMBNAILS_API = "https://thumbnails.roblox.com/v1"


def _get_json(url: str, method: str = "GET", json_body: dict | None = None):
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.request(method, url, json=json_body, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Upstream error: {exc}") from exc


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/user")
async def get_user(query: str):
    query = query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # If query looks like a user id (digits only), use it directly
    if query.isdigit():
        user_id = int(query)
    else:
        # Resolve username to id
        username_payload = {"usernames": [query], "excludeBannedUsers": False}
        data = _get_json(f"{ROBLOX_USERS_API}/usernames/users", method="POST", json_body=username_payload)
        if not data.get("data"):
            raise HTTPException(status_code=404, detail="User not found")
        user_id = data["data"][0]["id"]

    user = _get_json(f"{ROBLOX_USERS_API}/users/{user_id}")

    # Public info endpoints
    friends_count = _get_json(f"{ROBLOX_FRIENDS_API}/users/{user_id}/friends/count")
    followers_count = _get_json(f"{ROBLOX_FRIENDS_API}/users/{user_id}/followers/count")
    following_count = _get_json(f"{ROBLOX_FRIENDS_API}/users/{user_id}/followings/count")

    groups = _get_json(f"{ROBLOX_GROUPS_API}/users/{user_id}/groups/roles")
    badges = _get_json(f"{ROBLOX_BADGES_API}/users/{user_id}/badges?limit=100&sortOrder=Asc")

    thumbnails = _get_json(
        f"{ROBLOX_THUMBNAILS_API}/users/avatar-headshot?userIds={user_id}&size=150x150&format=Png&isCircular=false"
    )
    avatar_url = None
    if thumbnails.get("data"):
        avatar_url = thumbnails["data"][0].get("imageUrl")

    return JSONResponse(
        {
            "user": user,
            "friends": friends_count,
            "followers": followers_count,
            "following": following_count,
            "groups": groups,
            "badges": badges,
            "avatar": avatar_url,
        }
    )
