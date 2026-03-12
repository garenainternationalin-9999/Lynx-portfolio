from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
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
    return templates.TemplateResponse("index.html", {"request": request})

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
