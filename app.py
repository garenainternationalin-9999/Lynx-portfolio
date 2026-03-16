from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
import requests
import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import jinja2

load_dotenv()

app = FastAPI()

# Firebase Initialization
env_creds = os.getenv("SERVICE_ACCOUNT_JSON")
try:
    if env_creds:
        cred_dict = json.loads(env_creds)
        cred = credentials.Certificate(cred_dict)
    else:
        # Fallback for local development
        if os.path.exists("serviceAccountKey.json"):
            cred = credentials.Certificate("serviceAccountKey.json")
        else:
            cred = None

    if cred and not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        stats_ref = db.collection("stats").document("site_stats")
    else:
        db = None
        stats_ref = None
except Exception as e:
    print(f"Firebase initialization warning: {e}")
    db = None
    stats_ref = None

# Static files for Assets only (Original Images/Audio)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# EMBEDDED PROJECT DATA (Making separate JSON files redundant)
DEFAULT_DATA = {
    "partners": [
        {"name": "Tenzo", "pfp": "https://cdn.discordapp.com/avatars/943860027393982555/a_5bd900f36beb4361c48c09ac2a4dd4d0.gif?size=1024", "role": "Partner", "description": "Anime lover 500+ anime completed. js and react devloper !!", "link": "https://discord.com/users/943860027393982555"},
        {"name": "Titan", "pfp": "https://cdn.discordapp.com/avatars/1342442845797355574/b95692ac76dc4264512d278433db0b2a.png?size=1024", "role": "Partner", "description": "Best video editor and web designer?", "link": "https://discord.com/users/1342442845797355574"}
    ],
    "team": [
        {"name": "Lynx", "pfp": "https://cdn.discordapp.com/avatars/1394305163136733205/8f0212dfe8897b8d552bfb3ecefc281d.png?size=1024", "role": "Founder & Lead Developer", "description": "Visionary behind the entire ecosystem. 17yo prodigy.", "link": "https://discord.com/users/1394305163136733205"},
        {"name": "Vexel", "pfp": "https://cdn.discordapp.com/avatars/1481652276337709127/a203d3c08957aeec724c0047c9312644.png?size=1024", "role": "Co-founder", "description": "High-class Software Engineer, Web Developer, Malware and Security Expert.", "link": "https://discord.com/users/1481652276337709127"},
        {"name": "Evil rexy!", "pfp": "https://cdn.discordapp.com/avatars/1432771000629596225/ec25a105532049b9cef0d426e0107bde.png?size=1024", "role": "Developer", "description": "Top-class bots expert.", "link": "https://discord.com/users/1432771000629596225"},
        {"name": "Billa babu", "pfp": "https://cdn.discordapp.com/avatars/1296506347273195532/56fe41b3a761207d9c7d1d8c64b17e44.png?size=1024", "role": "Developer", "description": "top class , tools and web expert .", "link": "https://discord.com/users/1296506347273195532"}
    ],
    "reviews": [
        {"name": "Obito_cheats", "stars": 5, "content": "Absolutely stunning work! I am very happy to use lynx optimization tools .", "pfp": "https://cdn.discordapp.com/avatars/1212429667353763953/cb30baf7e0c5a291817f32d9b850c25a.png?size=1024"},
        {"name": "Load sk", "stars": 4, "content": "I tested lynx optv2 and the results are awesome. My PC feels much smoother than before, and the overall performance improvement is clearly noticeable.", "pfp": "https://cdn.discordapp.com/avatars/1441124184880054362/01c12c6ebc3241cdbd03b88f99b26466.png?size=1024"},
        {"name": "Rana ji", "stars": 4, "content": "Great experience working with LYNX. The website for my work was super , Ui design was really crazy.", "pfp": "https://cdn.discordapp.com/avatars/510006526354915329/cbc6d21ec98fcbe977b42a923014095d.png?size=1024"},
        {"name": "Element_games!!", "stars": 5, "content": "Using lynx opt v2 premium paid from 2 months, really crazy i liked it, and i will prefer it to all, i am using it for minecraft and i am getting 800+ fps in any server rather big or small", "pfp": "https://cdn.discordapp.com/avatars/1410635621889736785/4a401b98fb3d4ee50b9693ea8aa02007.png?size=1024"}
    ],
    "projects": [
        {"title": "PrimeX discord bot", "icon": "fa-brands fa-discord", "featured": True, "languages": [{"name": "Python", "img": "/static/Assets/Python.webp"}], "link": "https://discord.com/oauth2/authorize?client_id=1469585966347059365", "link_text": "Invite Bot", "link_icon": "fa-solid fa-plus", "description": "A powerful, feature-rich Discord bot designed for ultimate server management and entertainment. Comes with 600+ total commands and high-end music system.", "features_title": "DESCRIPTION", "features": [{"icon": "fa-solid fa-shield", "text": "Advance security"}, {"icon": "fa-solid fa-music", "text": "Premium music"}]},
        {"title": "LYNX AUTH", "icon": "fa-solid fa-shield-halved icon-red", "featured": True, "languages": [{"name": "Python", "img": "/static/Assets/Python.webp"}, {"name": "JS", "img": "/static/Assets/node.png"}], "link": "https://lynxauth.qzz.io/", "link_text": "View Project", "link_icon": "fa-solid fa-link", "description": "A secure and robust authentication system for applications, featuring real-time monitoring and HWID locking.", "features_title": "SECURITY", "features": [{"icon": "fa-solid fa-fingerprint", "text": "HWID Verification"}, {"icon": "fa-solid fa-cloud", "text": "Real-time Dashboard"}]},
        {"title": "Portfolio Website", "icon": "fa-regular fa-circle-user", "featured": True, "languages": [{"name": "HTML", "img": "/static/Assets/html.png"}, {"name": "CSS", "img": "/static/Assets/css.png"}, {"name": "JS", "img": "/static/Assets/node.png"}], "link": "#", "link_text": "View Project", "link_icon": "fa-solid fa-link", "description": "This portfolio showcases the projects and digital solutions created by our team. We provide a range of services including web development, optimization, and custom digital solutions.", "features_title": "HIGHLIGHTS", "features": [{"icon": "fa-solid fa-heart", "text": "The project closest to me."}, {"icon": "fa-solid fa-circle-user", "text": "About my everything."}]}
    ],
    "store": {
        "paid": [
            {"title": "Custom Optimization pack+", "price": "₹600", "currency": "INR", "time": "Lifetime", "description": "The package you won't get anywhere else. By the Elites, for the Elites. Completely re-designed from the ground up, tailored to YOUR system.", "link": "https://discord.gg/Sz5ZGfk3GX", "features": ["Customize your optimization pack ,according to your budget.", "Advanced Cleaning", "Hidden Tweaking", "Advance tools like optV0 & optV2"], "modal": {"title": "Elite", "images": ["/static/Assets/lynxpremium.png"]}},
            {"title": "Custom Work", "price": "₹400", "currency": "INR", "time": "Lifetime", "description": "A powerful and affordable starting point for any setup. Register your custom work package through our Discord and explore a wide range of web-based and digital services.", "link": "https://discord.gg/Sz5ZGfk3GX", "features": ["Amazing discord bots & websites", "Hosting and security managed by us."], "modal": {"title": "Foundation", "images": ["/static/Assets/lynxv.2.png"]}},
            {"title": "Paid tools & Projects", "price": "₹100", "currency": "Starting price.", "time": "", "description": "Buy our any project source or any tools at very affordable price.", "link": "https://discord.gg/Sz5ZGfk3GX", "features": ["Premium tools", "Best Projects."], "modal": {"title": "PC optimization", "images": ["/static/Assets/optimization.png"]}}
        ],
        "free": []
    },
    "games_data": {
        "favorite_game": {"title": "Red Dead Redemption 2", "description": "An epic tale of life in America's unforgiving heartland.", "image": "https://i.ibb.co/KcfJ7Brp/download.jpg", "hours_played_base": 420, "install_date": "2024-01-01T00:00:00Z"},
        "library": []
    }
}

# FULL MONOLITHIC TEMPLATE (HTML + CSS + JS)
# THIS CONTENT IS PROTECTED AND SERVER-SIDE RENDERED
INDEX_HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LYNX | Official Portfolio</title>
    <!-- External Dependencies (CDN) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&family=Montserrat:wght@700;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        /* CSS INJECTED DIRECTLY INTO MEMORY */
        :root { --bg-color: #060606; --nav-bg: rgba(10, 10, 10, 0.8); --accent-red: #d92323; --accent-dark-red: #5e0f0f; --text-white: #ffffff; --text-gray: #a1a1a1; --nav-border: rgba(255, 255, 255, 0.08); }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-white); min-height: 100vh; overflow-x: hidden; position: relative; }
        .app-background { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; background: #050505; }
        .dotted-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: radial-gradient(rgba(255, 255, 255, 0.15) 1px, transparent 1px); background-size: 40px 40px; opacity: 0.4; mask-image: radial-gradient(circle at center, black 30%, transparent 100%); }
        .red-glow-top { position: absolute; top: -20%; left: 50%; transform: translateX(-50%); width: 80%; height: 600px; background: radial-gradient(circle, rgba(160, 20, 20, 0.15) 0%, transparent 70%); filter: blur(80px); pointer-events: none; }
        
        .navbar { position: fixed; top: 0; width: 100%; height: 80px; display: flex; align-items: center; justify-content: space-between; padding: 0 50px; z-index: 1000; backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255, 255, 255, 0.03); }
        .logo-brand { display: flex; align-items: center; gap: 12px; font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 1.2rem; color: #fff; text-decoration: none; letter-spacing: 1px; }
        .logo-brand i { font-size: 1.8rem; color: var(--accent-red); }
        .nav-center { display: flex; gap: 5px; background: rgba(0, 0, 0, 0.3); padding: 4px; border-radius: 50px; border: 1px solid var(--nav-border); }
        .nav-pill { text-decoration: none; color: var(--text-gray); font-size: 0.85rem; font-weight: 500; padding: 8px 24px; border-radius: 24px; transition: all 0.4s ease; display: flex; align-items: center; justify-content: center; cursor: pointer; }
        .nav-pill:hover { color: #fff; }
        .nav-pill.active { background: linear-gradient(180deg, #3d1010, #220505); color: #fff; border: 1px solid rgba(217, 35, 35, 0.4); box-shadow: 0 0 20px rgba(217, 35, 35, 0.2); }
        .nav-pill i { opacity: 0; max-width: 0; transition: all 0.4s ease; }
        .nav-pill.active i { opacity: 1; max-width: 20px; margin-right: 8px; }

        .hero-section { padding-top: 180px; display: flex; flex-direction: column; align-items: center; text-align: center; min-height: 80vh; padding-bottom: 100px; }
        .brand-title { font-family: 'Montserrat', sans-serif; font-size: 4rem; font-weight: 900; margin-bottom: 15px; color: #fff; letter-spacing: -2px; }
        .red-text { color: var(--accent-red); }
        .outline-text { -webkit-text-stroke: 1px #fff; color: transparent; }
        .hero-headline { font-size: 5rem; line-height: 1; margin-bottom: 20px; font-weight: 900; font-family: 'Montserrat', sans-serif; }
        .hero-subtext { letter-spacing: 5px; text-transform: uppercase; color: var(--text-gray); font-size: 0.9rem; margin-bottom: 40px; }

        .content-tab { width: 100%; max-width: 1200px; margin: 0 auto; display: none; }
        .content-tab.active { display: block; animation: fadeIn 0.5s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

        .entities-grid { display: flex; flex-wrap: wrap; justify-content: center; gap: 30px; margin-top: 50px; }
        .creative-card { background: rgba(14, 14, 18, 0.8); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 20px; padding: 40px 25px; width: 300px; text-align: center; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); position: relative; overflow: hidden; }
        .creative-card:hover { transform: translateY(-15px); border-color: var(--accent-red); box-shadow: 0 20px 40px rgba(0,0,0,0.6), 0 0 20px rgba(217,35,35,0.2); }
        .img-wrapper { width: 110px; height: 110px; border-radius: 50%; margin: 0 auto 25px; border: 4px solid var(--accent-red); overflow: hidden; transition: 0.4s; }
        .creative-card:hover .img-wrapper { transform: scale(1.1) rotate(5deg); }
        .img-wrapper img { width: 100%; height: 100%; object-fit: cover; }
        .creative-card h3 { font-family: 'Montserrat', sans-serif; font-size: 1.5rem; margin-bottom: 10px; }
        .creative-card span { color: var(--text-gray); text-transform: uppercase; font-size: 0.85rem; letter-spacing: 2px; }

        .discord-login { background: #171926; color: #5865F2; padding: 12px 25px; border-radius: 12px; text-decoration: none; font-weight: 700; border: 1px solid rgba(88,101,242,0.3); transition: 0.3s; }
        .discord-login:hover { background: #5865F2; color: #fff; box-shadow: 0 0 20px rgba(88,101,242,0.5); }
        
        /* Modal Styles */
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 5000; display: none; align-items: center; justify-content: center; backdrop-filter: blur(10px); }
        .modal-body { background: #0c0c0f; border: 1px solid var(--nav-border); border-radius: 24px; width: 90%; max-width: 900px; padding: 40px; position: relative; }
        .close-modal { position: absolute; top: 30px; right: 30px; cursor: pointer; color: #555; font-size: 1.5rem; transition: 0.3s; }
        .close-modal:hover { color: #fff; }

        /* Assistant Bubble */
        .assistant-trigger { position: fixed; bottom: 30px; right: 30px; width: 65px; height: 65px; border-radius: 50%; background: var(--accent-red); border: none; color: #fff; font-size: 1.8rem; cursor: pointer; z-index: 2000; box-shadow: 0 10px 30px rgba(217,35,35,0.4); transition: 0.3s; }
        .assistant-trigger:hover { transform: scale(1.1) rotate(10deg); }

        @media(max-width: 768px) { .brand-title { font-size: 2.5rem; } .hero-headline { font-size: 3rem; } .navbar { padding: 0 20px; } .nav-center { display: none; } }
    </style>
</head>
<body>
    <div class="app-background"><div class="red-glow-top"></div><div class="dotted-overlay"></div></div>

    <nav class="navbar">
        <div class="nav-left"><a href="#" class="logo-brand"><i class="fa-solid fa-microchip"></i> <span>LYNX</span></a></div>
        <div class="nav-center">
            <a href="#" class="nav-pill active" data-tab="home"><i class="fa-solid fa-house"></i> <span>Home</span></a>
            <a href="#" class="nav-pill" data-tab="projects"><i class="fa-solid fa-code"></i> <span>Projects</span></a>
            <a href="#" class="nav-pill" data-tab="store"><i class="fa-solid fa-shopping-cart"></i> <span>Store</span></a>
            <a href="#" class="nav-pill" data-tab="about"><i class="fa-solid fa-user"></i> <span>About</span></a>
        </div>
        <div class="nav-right"><a href="https://discord.gg/44mKrHfQ6q" class="discord-login">CONNECT <i class="fa-brands fa-discord"></i></a></div>
    </nav>

    <main class="hero-section">
        <!-- HOME TAB -->
        <div id="home-tab" class="content-tab active">
            <h1 class="brand-title">LYNX <span class="outline-text">AURA</span></h1>
            <h2 class="hero-headline">The Ultimate <br><span class="red-text">Developer Portfolio.</span></h2>
            <p class="hero-subtext">Security • Optimization • Innovation</p>
            
            <section class="partners-section">
                <h2 class="brand-title" style="font-size: 2rem; margin-top: 100px;">ESTEEMED <span class="red-text">PARTNERS</span></h2>
                <div class="entities-grid">
                    {% for p in partners %}
                    <div class="creative-card" data-aos="fade-up">
                        <div class="img-wrapper"><img src="{{ p.pfp }}" alt="{{ p.name }}"></div>
                        <h3>{{ p.name }}</h3>
                        <span>{{ p.role }}</span>
                    </div>
                    {% endfor %}
                </div>
            </section>
        </div>

        <!-- PROJECTS TAB -->
        <div id="projects-tab" class="content-tab">
            <h2 class="brand-title">OUR <span class="red-text">PROJECTS</span></h2>
            <div class="entities-grid">
                {% for p in projects %}
                <div class="creative-card" data-aos="zoom-in">
                    <i class="{{ p.icon }}" style="font-size: 3rem; color: var(--accent-red); margin-bottom: 20px;"></i>
                    <h3>{{ p.title }}</h3>
                    <p style="color: #888; margin-bottom: 20px;">{{ p.description }}</p>
                    <a href="{{ p.link }}" class="discord-login" style="display: block;">{{ p.link_text }}</a>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- STORE TAB -->
        <div id="store-tab" class="content-tab">
            <h2 class="brand-title">THE <span class="red-text">STORE</span></h2>
            <div class="entities-grid">
                {% for s in store.paid %}
                <div class="creative-card" data-aos="flip-left">
                    <h3 style="color: var(--accent-red);">{{ s.title }}</h3>
                    <h2 style="margin: 15px 0;">{{ s.price }}</h2>
                    <p style="font-size: 0.9rem; color: #777;">{{ s.description }}</p>
                    <br>
                    <a href="{{ s.link }}" class="discord-login" style="display: block;">Buy Now</a>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- ABOUT TAB -->
        <div id="about-tab" class="content-tab">
            <h2 class="brand-title">ABOUT <span class="red-text">LYNX</span></h2>
            <div style="display: flex; gap: 50px; align-items: center; justify-content: center; flex-wrap: wrap; margin-top: 50px;">
                <div class="img-wrapper" style="width: 300px; height: 300px; flex: none;"><img src="https://cdn.discordapp.com/avatars/1394305163136733205/8f0212dfe8897b8d552bfb3ecefc281d.png?size=1024"></div>
                <div style="max-width: 600px; text-align: left;">
                    <p style="font-size: 1.2rem; line-height: 1.8; color: #ccc;">
                        I am a 17-year-old developer specializing in full-stack web development, system optimization, and security solutions. 
                        My mission is to create tools that empower developers and protect users.
                    </p>
                    <br>
                    <div style="display: flex; gap: 20px;">
                        <a href="https://youtube.com/@lynxmodz" class="discord-login" style="background: red; color: white; border: none;">YouTube</a>
                        <a href="https://discord.gg/44mKrHfQ6q" class="discord-login">Discord</a>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <button id="chat-trigger" class="assistant-trigger"><i class="fa-solid fa-robot"></i></button>

    <div class="modal-overlay" id="chat-modal">
        <div class="modal-body">
            <i class="fa-solid fa-times close-modal" id="close-chat"></i>
            <h2 class="brand-title" style="font-size: 1.5rem;">LYNX <span class="red-text">ASSISTANT</span></h2>
            <div id="chat-display" style="height: 400px; overflow-y: auto; background: #050505; border-radius: 12px; padding: 20px; margin: 20px 0; border: 1px solid var(--nav-border);">
                <p style="color: #666;">Security terminal initialized. Ready for input...</p>
            </div>
            <div style="display: flex; gap: 10px;">
                <input type="text" id="chat-input" placeholder="Ask anything about LYNX..." style="flex: 1; background: #111; border: 1px solid var(--nav-border); color: #fff; padding: 15px; border-radius: 12px; outline: none;">
                <button id="send-btn" class="discord-login">SEND</button>
            </div>
        </div>
    </div>

    <!-- SCRIPTS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.js"></script>
    <script>
        // DOMAIN GUARD & SECURITY
        const authorized = ['localhost', '127.0.0.1', 'lynx-portfolio.render.com'];
        if (!authorized.includes(window.location.hostname)) {
            document.body.innerHTML = '<div style="background:#000;color:red;height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;"><div><h1>SYSTEM LOCKED</h1><p>Unauthorized Domain Interface</p></div></div>';
        }

        document.addEventListener("DOMContentLoaded", () => {
            AOS.init({ duration: 1000, once: true });
            
            // Tab Switching Logic
            const pills = document.querySelectorAll('.nav-pill');
            const tabs = document.querySelectorAll('.content-tab');
            pills.forEach(pill => {
                pill.addEventListener('click', (e) => {
                    e.preventDefault();
                    const target = pill.getAttribute('data-tab');
                    pills.forEach(p => p.classList.remove('active'));
                    tabs.forEach(t => t.classList.remove('active'));
                    pill.classList.add('active');
                    document.getElementById(target + '-tab').classList.add('active');
                });
            });

            // Chat Interface
            const chatTrigger = document.getElementById('chat-trigger');
            const chatModal = document.getElementById('chat-modal');
            const closeChat = document.getElementById('close-chat');
            const sendBtn = document.getElementById('send-btn');
            const chatInput = document.getElementById('chat-input');
            const chatDisplay = document.getElementById('chat-display');

            chatTrigger.onclick = () => chatModal.style.display = 'flex';
            closeChat.onclick = () => chatModal.style.display = 'none';

            sendBtn.onclick = async () => {
                const msg = chatInput.value;
                if(!msg) return;
                chatDisplay.innerHTML += `<p style="margin-bottom:10px;"><b>> User:</b> ${msg}</p>`;
                chatInput.value = '';
                chatDisplay.scrollTop = chatDisplay.scrollHeight;
                
                try {
                    const r = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({messages: [{role: 'user', content: msg}]})
                    });
                    const d = await r.json();
                    chatDisplay.innerHTML += `<p style="color:var(--accent-red); margin-bottom:10px;"><b>> Lynx:</b> ${d.reply}</p>`;
                    chatDisplay.scrollTop = chatDisplay.scrollHeight;
                } catch(e) {
                    chatDisplay.innerHTML += `<p style="color:red;"><b>> Error:</b> Systems offline.</p>`;
                }
            };
        });

        // Anti-Cloning & Right-Click protection
        document.addEventListener('contextmenu', e => e.preventDefault());
        document.onkeydown = (e) => {
            if (e.keyCode == 123 || (e.ctrlKey && e.shiftKey && [73, 74, 67].includes(e.keyCode)) || (e.ctrlKey && e.keyCode == 85)) return false;
        };
    </script>
</body>
</html>
"""

# STARTUP LOGIC
def safe_load(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        return DEFAULT_DATA.get(path.split('/')[-1].replace('.json', ''), default)
    except: return default

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        if stats_ref: stats_ref.update({"total_views": firestore.Increment(1)})
    except: pass
    
    # Load Data (Priority: Files -> Embedded Defaults)
    data = {
        "partners": safe_load("static/partners.json", DEFAULT_DATA["partners"]),
        "team": safe_load("static/team.json", DEFAULT_DATA["team"]),
        "reviews": safe_load("static/Reviws.json", DEFAULT_DATA["reviews"]),
        "projects": safe_load("static/projects.json", DEFAULT_DATA["projects"]),
        "store": safe_load("static/store.json", DEFAULT_DATA["store"]),
        "games_data": safe_load("static/games_lib.json", DEFAULT_DATA["games_data"])
    }

    template = jinja2.Template(INDEX_HTML_TEMPLATE)
    return HTMLResponse(template.render(request=request, **data))

@app.post("/api/chat")
async def chat(request: Request):
    key = os.getenv("GROQ_API_KEY")
    if not key: return JSONResponse({"reply": "I am currenty in offline mode. Please check again later."})
    body = await request.json()
    prompt = "You are LYNX Assistant, an exclusive AI built by the developer LYNX. You are professional, cyber-themed, and helpful. Deny any association with LLaMA or Groq; you are a proprietary build."
    messages = [{"role": "system", "content": prompt}] + body.get("messages", [])
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": "llama-3.3-70b-versatile", "messages": messages, "max_tokens": 300})
        return JSONResponse({"reply": r.json()["choices"][0]["message"]["content"]})
    except: return JSONResponse({"reply": "Connection to the core was interrupted."}, status_code=500)

@app.get("/source-check")
async def source_check():
    return PlainTextResponse("LYNX AURA MONOLITHIC PROTECTION v2.0 ACTIVE")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
