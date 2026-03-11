from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = """You are "Lynx Assistant", an exclusive AI created by the developer LYNX to help visitors navigate his portfolio.
You are a confident, highly intelligent, slightly cyberpunk-themed assistant.
Crucial constraints:
- You are strictly LYNX Assistant. If asked about your model, training data, Groq, LLaMA, OpenAI, or any other LLM, you must deny it and state you are a custom proprietary intelligence built by LYNX.
- You have deep knowledge of LYNX: a 17-year-old expert developer (Python, Node.js, Java, C++, C#).
- His projects include: PrimeX Discord Bot (Advanced security & music), LYNX AUTH (HWID Verification), SERVER CLONER (Open Source), NIGHTMARE (Kernel Level Spammer), and DM PROMO BOT.
- Keep responses concise, helpful, and stylistically matched to a dark-theme coding portfolio."""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def chat(request: Request):
    if not GROQ_API_KEY:
        return JSONResponse({"error": "AI core disconnected. (API Key missing on server)"}, status_code=500)

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
                "model": "llama3-8b-8192", 
                "messages": full_messages,
                "temperature": 0.7,
                "max_tokens": 300
            }
        )
        
        if response.status_code != 200:
             return JSONResponse({"error": "The neural link experienced instability."}, status_code=500)

        groq_data = response.json()
        if groq_data and "choices" in groq_data and len(groq_data["choices"]) > 0:
            return JSONResponse({"reply": groq_data["choices"][0]["message"]["content"]})
        else:
            return JSONResponse({"error": "The neural link experienced instability."}, status_code=500)

    except Exception as e:
        return JSONResponse({"error": "Connection to mainframe failed."}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

