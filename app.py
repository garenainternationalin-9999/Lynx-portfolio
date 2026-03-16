from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import os
import json
import asyncio
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

app = FastAPI()


env_creds = os.getenv("SERVICE_ACCOUNT_JSON")

try:
    if env_creds:
        cred_dict = json.loads(env_creds)
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate("serviceAccountKey.json")

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    stats_ref = db.collection("stats").document("site_stats")

except Exception as e:
    raise RuntimeError(f"Firebase initialization failed: {e}")


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

connected_clients = set()

async def get_current_stats():
    doc = stats_ref.get()

    if not doc.exists:
        stats_ref.set({
            "total_views": 0,
            "total_likes": 0
        })
        return {"total_views": 0, "total_likes": 0}

    return doc.to_dict()

async def broadcast_stats():
    stats = await get_current_stats()
    data = {
        "total_views": stats.get("total_views", 0),
        "total_likes": stats.get("total_likes", 0)
    }
    
    if not connected_clients:
        return

    disconnected = set()
    for ws in connected_clients:
        try:
            await ws.send_json(data)
        except Exception:
            disconnected.add(ws)
    connected_clients.difference_update(disconnected)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Stats logic
    doc = stats_ref.get()

    if not doc.exists:
        stats_ref.set({
            "total_views": 1,
            "total_likes": 0
        })
    else:
        stats_ref.update({
            "total_views": firestore.Increment(1)
        })

    asyncio.create_task(broadcast_stats())

    # Load data from JSON files
    try:
        with open("static/partners.json", "r", encoding="utf-8") as f:
            partners = json.load(f)
        with open("static/team.json", "r", encoding="utf-8") as f:
            team = json.load(f)
        with open("static/Reviws.json", "r", encoding="utf-8") as f:
            reviews = json.load(f)
        with open("static/games_lib.json", "r", encoding="utf-8") as f:
            games_data = json.load(f)
        with open("static/projects.json", "r", encoding="utf-8") as f:
            projects = json.load(f)
        with open("static/store.json", "r", encoding="utf-8") as f:
            store = json.load(f)
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        partners, team, reviews, games_data, projects, store = [], [], [], {}, [], {}

    # Calculate hours for games
    from datetime import datetime
    def calculate_hours(base, install_date_str):
        try:
            install_date = datetime.fromisoformat(install_date_str.replace('Z', '+00:00'))
            now = datetime.now(install_date.tzinfo)
            diff_days = (now - install_date).days
            return base + diff_days
        except:
            return base

    if games_data:
        fav = games_data.get('favorite_game', {})
        if fav:
            fav['hours_played'] = calculate_hours(fav.get('hours_played_base', 0), fav.get('install_date', ''))
        
        for game in games_data.get('library', []):
            game['hours_played'] = calculate_hours(game.get('hours_played_base', 0), game.get('install_date', ''))

    return templates.TemplateResponse("index.html", {
        "request": request,
        "partners": partners,
        "team": team,
        "reviews": reviews,
        "games_data": games_data,
        "projects": projects,
        "store": store
    })

@app.get("/api/views")
async def get_views_api():
    stats = await get_current_stats()
    return JSONResponse({
        "total_views": stats.get("total_views", 0),
        "total_likes": stats.get("total_likes", 0)
    })

@app.post("/api/like")
async def add_like():
    stats_ref.update({
        "total_likes": firestore.Increment(1)
    })

    await broadcast_stats()
    return JSONResponse({"status": "success"})

@app.websocket("/ws/views")
async def websocket_views(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        stats = await get_current_stats()
        await websocket.send_json({
            "total_views": stats.get("total_views", 0),
            "total_likes": stats.get("total_likes", 0)
        })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.discard(websocket)
    except Exception:
        connected_clients.discard(websocket)


SYSTEM_PROMPT = """You are "Lynx Assistant", an exclusive AI created by the developer LYNX to help visitors navigate his portfolio.
You are a confident, highly intelligent, slightly cyberpunk-themed assistant.
Crucial constraints:
- You are strictly LYNX Assistant. If asked about your model, training data, Groq, LLaMA, OpenAI, or any other LLM, you must deny it and state you are a custom proprietary intelligence built by LYNX.
- You have deep knowledge of LYNX: a 17-year-old expert developer (Python, Node.js, Java, C++, C#).
- His projects include: PrimeX Discord Bot (Advanced security & music), LYNX AUTH (HWID Verification), And his pro.
- Keep responses concise, helpful, and stylistically matched to a dark-theme coding portfolio website."""

@app.post("/api/chat")
async def chat(request: Request):
    if not GROQ_API_KEY:
        return JSONResponse({"error": "AI core disconnected."}, status_code=500)

    data = await request.json()
    messages = data.get("messages", [])
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile", 
                "messages": full_messages,
                "temperature": 0.7,
                "max_tokens": 300
            }
        )
        groq_data = response.json()
        return JSONResponse({"reply": groq_data["choices"][0]["message"]["content"]})
    except Exception as e:
        return JSONResponse({"error": "Connection to mainframe failed."}, status_code=500)

@app.get("/source-check")
async def source_check():
    try:
        with open("src_check.js", "r", encoding="utf-8") as f:
            content = f.read()
        return PlainTextResponse(content)
    except Exception as e:
        return PlainTextResponse(f"Error reading file: {e}", status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
