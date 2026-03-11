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
- You have deep knowledge of LYNX: a 17-year-old expert developer (Python, Node.js, Java, C++, C
- His projects include: PrimeX Discord Bot (Advanced security & music), LYNX AUTH (HWID Verification), SERVER CLONER (Open Source), NIGHTMARE (Kernel Level Spammer), and DM PROMO BOT.
- Keep responses concise, helpful, and stylistically matched to a dark-theme coding portfolio."""

PROJECTS = [
    {
        "id": "primex",
        "title": "PrimeX discord bot",
        "icon": "fa-brands fa-discord",
        "featured": True,
        "languages": [{"name": "Python", "img": "Python.webp"}],
        "link": "https://discord.gg/44mKrHfQ6q",
        "link_text": "Invite Bot",
        "desc": "A powerful, feature-rich Discord bot designed for ultimate server management and entertainment.",
        "feature_title": "DESCRIPTION",
        "features": [
            {"icon": "fa-solid fa-shield", "text": "Advance security"},
            {"icon": "fa-solid fa-music", "text": "Premium music"}
        ]
    },
    {
        "id": "lynxauth",
        "title": "LYNX AUTH",
        "icon": "fa-solid fa-shield-halved icon-red",
        "featured": True,
        "languages": [
            {"name": "Python", "img": "Python.webp"},
            {"name": "JS", "img": "node.png"}
        ],
        "link": "https://lynxauth.qzz.io/",
        "link_text": "View Project",
        "desc": "A secure and robust authentication system for applications, featuring real-time monitoring and HWID locking.",
        "feature_title": "SECURITY",
        "features": [
            {"icon": "fa-solid fa-fingerprint", "text": "HWID Verification"},
            {"icon": "fa-solid fa-cloud", "text": "Real-time Dashboard"}
        ]
    },
    {
        "id": "portfolio",
        "title": "Portfolio Website",
        "icon": "fa-regular fa-circle-user",
        "featured": True,
        "languages": [
            {"name": "HTML", "img": "html.png"},
            {"name": "CSS", "img": "css.png"},
            {"name": "JS", "img": "node.png"}
        ],
        "link": "
        "link_text": "View Project",
        "desc": "My personal portfolio website designed with a premium, dark-themed aesthetic and high-performance animations.",
        "feature_title": "HIGHLIGHTS",
        "features": [
            {"icon": "fa-solid fa-heart", "text": "The project closest to me."},
            {"icon": "fa-solid fa-circle-user", "text": "About my everything."}
        ]
    }
]

EXTRA_PROJECTS = [
    {
        "title": "SERVER CLONER",
        "icon": "fas fa-bolt icon-gold",
        "type": "paragon",
        "badge": "Open Source",
        "badge_icon": "fa-solid fa-code-branch",
        "desc": "An opensource project of servercloner tool, created on python. find it on my discord server",
        "link": "https://discord.gg/Sz5ZGfk3GX",
        "link_text": "Download",
        "btn_class": "btn-gold",
        "features": [{"icon": "fa-solid fa-box-open", "text": "Full Open Source"}]
    },
    {
        "title": "NIGHTMARE",
        "icon": "fa-solid fa-ghost",
        "type": "nightmare",
        "badge": "BETA 0.0",
        "sub": "Kernel Level Spammer",
        "desc": "Discord selfbot spammer tool, created under some restrictions and still under beta version.",
        "link": "services/NIGHTMARE.zip",
        "link_text": "Download",
        "btn_class": "nightmare-btn",
        "features": [{"icon": "fa-solid fa-robot", "text": "Self Bot Spammer"}]
    },
    {
        "title": "DM PROMO BOT",
        "icon": "fa-solid fa-cloud icon-red",
        "type": "paragon",
        "desc": "A fast and reliable automated DM promotional tool for expanding your reach effortlessly.",
        "link": "https://dm-bot-web-service.onrender.com/",
        "link_text": "Run Now",
        "btn_class": "btn-primary",
        "features": [{"icon": "fa-solid fa-bolt", "text": "Fast & Reliable"}]
    }
]

REVIEWS = [
    {"img": "review8.png", "rating": "5.0"},
    {"img": "review7.png", "rating": "4.9"},
    {"img": "review6.png", "rating": "4.8"},
    {"img": "review5.png", "rating": "5.0"},
    {"img": "review1.png", "rating": "5.0"},
    {"img": "review2.png", "rating": "4.9"},
    {"img": "review3.png", "rating": "4.8"},
    {"img": "review4.png", "rating": "5.0"}
]

DIARY_DATA = {
    "thoughts": [
        "Code is like poetry; most people don't understand it.",
        "Stability is not just code, it's a mindset.",
        "Building the future, one line at a time.",
        "Efficiency is the ultimate sophistication."
    ],
    "goals": [
        "Mastering decentralized intelligence.",
        "Reaching 100k+ active users on PrimeX.",
        "Developing a full-scale BOT.",
        "Optimizing every millisecond of performance."
    ],
    "feelings": [
        "Fueled by dark mode and caffeine.",
        "Determined to break the simulation.",
        "Feeling the aura of peak development.",
        "Syncing with the mainframe..."
    ]
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "main_projects": PROJECTS,
        "extra_projects": EXTRA_PROJECTS,
        "reviews": REVIEWS,
        "diary": DIARY_DATA
    })

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
                "model": "llama-3.3-70b-versatile", 
                "messages": full_messages,
                "temperature": 0.7,
                "max_tokens": 300
            }
        )
        
        if response.status_code != 200:
             return JSONResponse({"error": f"The neural link experienced instability. (Status: {response.status_code}, Body: {response.text})"}, status_code=500)

        groq_data = response.json()
        if groq_data and "choices" in groq_data and len(groq_data["choices"]) > 0:
            return JSONResponse({"reply": groq_data["choices"][0]["message"]["content"]})
        else:
            return JSONResponse({"error": f"The neural link experienced instability. (Data: {groq_data})"}, status_code=500)

    except Exception as e:
        return JSONResponse({"error": f"Connection to mainframe failed: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

