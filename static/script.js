document.addEventListener("DOMContentLoaded", () => {
    const navItems = document.querySelectorAll('.nav-pill');

    const homeContent = document.getElementById('home-content');
    const aboutContent = document.getElementById('about-content');
    const servicesContent = document.getElementById('services-content');
    const storeContent = document.getElementById('store-content');
    const othersContent = document.getElementById('others-content');
    const resourcesContent = document.getElementById('resources-content');

    function switchTab(id) {
        navItems.forEach(nav => nav.classList.remove('active'));

        const activeBtn = document.querySelector(`.nav-pill[data-id="${id}"]`);
        if (activeBtn) activeBtn.classList.add('active');

        if (homeContent) homeContent.style.display = 'none';
        if (aboutContent) aboutContent.style.display = 'none';
        if (servicesContent) servicesContent.style.display = 'none';
        if (storeContent) storeContent.style.display = 'none';
        if (othersContent) othersContent.style.display = 'none';
        if (resourcesContent) resourcesContent.style.display = 'none';

        if (id === 'home') {
            if (homeContent) homeContent.style.display = 'block';
        } else if (id === 'about') {
            if (aboutContent) aboutContent.style.display = 'block';
        } else if (id === 'services') {
            if (servicesContent) servicesContent.style.display = 'block';
        } else if (id === 'store') {
            if (storeContent) storeContent.style.display = 'block';
        } else if (id === 'others') {
            if (othersContent) othersContent.style.display = 'block';
        } else if (id === 'resources') {
            if (resourcesContent) resourcesContent.style.display = 'block';
        }
    }

    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const id = this.getAttribute('data-id');
            if (['home', 'about', 'services', 'store', 'others', 'resources'].includes(id)) {
                switchTab(id);
            }
        });
    });

    const hamburgerBtn = document.getElementById('hamburger-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-link');

    if (hamburgerBtn && mobileMenu) {
        hamburgerBtn.addEventListener('click', () => {
            if (mobileMenu.style.display === 'flex') {
                mobileMenu.style.display = 'none';
                hamburgerBtn.innerHTML = '<i class="fa-solid fa-bars"></i>';
            } else {
                mobileMenu.style.display = 'flex';
                hamburgerBtn.innerHTML = '<i class="fa-solid fa-xmark"></i>';
            }
        });

        mobileLinks.forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                const id = this.getAttribute('data-id');
                if (['home', 'about', 'services', 'store', 'others', 'resources'].includes(id)) {
                    switchTab(id);
                    mobileMenu.style.display = 'none';
                    hamburgerBtn.innerHTML = '<i class="fa-solid fa-bars"></i>';
                }
            });
        });
    }
});

let currentImages = [];
let currentIndex = 0;
const modal = document.getElementById('image-modal');
const modalImg = document.getElementById('modal-img');
const modalTitle = document.getElementById('modal-title');

function openModal(title, images) {
    if (!modal) return;

    modalTitle.innerText = title;
    currentImages = images;
    currentIndex = 0;

    if (currentImages.length > 0) {
        modalImg.src = currentImages[0];
    } else {
        modalImg.src = '';
    }

    modal.style.display = 'flex';
}

function closeModal() {
    if (modal) modal.style.display = 'none';
}

function changeImage(direction) {
    if (currentImages.length === 0) return;

    currentIndex += direction;

    if (currentIndex < 0) {
        currentIndex = currentImages.length - 1;
    } else if (currentIndex >= currentImages.length) {
        currentIndex = 0;
    }

    modalImg.src = currentImages[currentIndex];
}

window.onclick = function (event) {
    if (event.target == modal) {
        closeModal();
    }
}

const API_URL = "https://api.lanyard.rest/v1/users/1394305163136733205";

async function fetchDiscordStatus() {
    const card = document.getElementById('discord-card');
    const pfp = document.getElementById('discord-pfp');
    const username = document.getElementById('discord-username');
    const activity = document.getElementById('discord-activity');
    const dot = document.getElementById('discord-status-dot');

    if (!card) return;

    try {
        const response = await fetch(API_URL);
        const jsonResponse = await response.json();

        if (!jsonResponse.success) {
            throw new Error("Lanyard API returned false success");
        }

        const data = jsonResponse.data;

        if (data.discord_user) {
            if (data.discord_user.username !== "User Not Monitored") {
                username.innerText = data.discord_user.username;
            } else {
                username.innerText = "LYNX";
            }

            if (data.discord_user.avatar && data.discord_user.avatar !== 'default') {
                pfp.src = `https://cdn.discordapp.com/avatars/${data.discord_user.id}/${data.discord_user.avatar}.png`;
            }
        }

        dot.className = 'status-dot';
        switch (data.discord_status) {
            case 'online': dot.classList.add('status-online'); break;
            case 'idle': dot.classList.add('status-idle'); break;
            case 'dnd': dot.classList.add('status-dnd'); break;
            default: dot.classList.add('status-offline');
        }

        if (data.discord_status === 'offline') {
            activity.innerText = "Offline";
            activity.style.color = "#777";
        } else {
            activity.style.color = "#ccc";
            if (data.activities && data.activities.length > 0) {
                let mainActivity = data.activities.find(act => act.type === 0) || data.activities[0];
                if (mainActivity.type === 0) activity.innerText = `Playing: ${mainActivity.name}`;
                else if (mainActivity.type === 4) activity.innerText = `Status: ${mainActivity.state || mainActivity.name}`;
                else activity.innerText = `Doing: ${mainActivity.name}`;
            } else {
                activity.innerText = "Online";
            }
        }

    } catch (error) {
        console.error("Fetch error:", error);
        activity.innerText = "Server Offline";
        dot.classList.add('status-offline');
    }
}

async function initReviews() {
    const reviewsContainer = document.getElementById('google-reviews-container');
    if (!reviewsContainer) return;

    try {
        const response = await fetch('/static/Reviws.json');
        const reviews = await response.json();

        reviewsContainer.innerHTML = reviews.map(review => `
            <div class="google-review-card" data-aos="fade-up">
                <div class="review-header">
                    <img src="${review.pfp}" alt="${review.name}" class="review-pfp">
                    <div class="review-meta">
                        <span class="review-author">${review.name}</span>
                        <div class="review-stars">
                            ${Array(5).fill(0).map((_, i) => `<i class="fa-solid fa-star ${i < review.stars ? 'active' : ''}"></i>`).join('')}
                        </div>
                    </div>
                </div>
                <p class="review-text">${review.content}</p>
                <div class="google-logo-mini">
                    <i class="fa-brands fa-google"></i>
                    <span>Verified</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error("Error loading reviews:", error);
        reviewsContainer.innerHTML = '<p class="error-text">Failed to load reviews mainframe link broken.</p>';
    }
}

document.addEventListener("DOMContentLoaded", () => {
    fetchDiscordStatus();
    setInterval(fetchDiscordStatus, 6000);
    initLynxAssistant();
    initReviews();
    initGamesLibrary();
    initMusicPlayer();
    initCustomCursor();
});

function initMusicPlayer() {
    const music = document.getElementById('bg-music');
    const toggleBtn = document.getElementById('music-toggle-btn');
    const volumeCtrl = document.getElementById('volume-control');
    const musicText = document.querySelector('.music-text');
    const icon = toggleBtn.querySelector('i');

    if (!music || !toggleBtn) return;

    music.volume = 0.5;

    const playMusic = () => {
        music.play().then(() => {
            icon.classList.replace('fa-play', 'fa-pause');
            musicText.innerText = "PAUSE BGM";
            document.removeEventListener('click', playMusic);
        }).catch(err => console.log("Autoplay blocked, waiting for interaction"));
    };

    document.addEventListener('click', playMusic);

    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (music.paused) {
            music.play();
            icon.classList.replace('fa-play', 'fa-pause');
            musicText.innerText = "PAUSE BGM";
        } else {
            music.pause();
            icon.classList.replace('fa-pause', 'fa-play');
            musicText.innerText = "PLAY BGM";
        }
    });

    volumeCtrl.addEventListener('input', (e) => {
        music.volume = e.target.value;
    });
}

function initCustomCursor() {
    window.addEventListener('mousedown', (e) => {
        const ripple = document.createElement('div');
        ripple.className = 'click-ripple';
        ripple.style.left = `${e.clientX}px`;
        ripple.style.top = `${e.clientY}px`;
        document.body.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 800);
    });
}

async function initGamesLibrary() {
    const root = document.getElementById('games-library-root');
    if (!root) return;

    try {
        const response = await fetch('/static/games_lib.json');
        const data = await response.json();

        const calculateHours = (base, date) => {
            const installDate = new Date(date);
            const now = new Date();
            const diffDays = Math.floor((now - installDate) / (1000 * 60 * 60 * 24));
            return base + diffDays;
        };

        const fav = data.favorite_game;
        const favHours = calculateHours(fav.hours_played_base, fav.install_date);

        let html = `
            <div class="fav-game-card" data-aos="fade-right">
                <div class="fav-badge">FAVOURITE GAME</div>
                <div class="fav-game-visual">
                    <img src="${fav.image}" alt="${fav.title}">
                    <div class="fav-overlay"></div>
                </div>
                <div class="fav-game-info">
                    <h3>${fav.title}</h3>
                    <p>${fav.description}</p>
                    <div class="fav-stats">
                        <div class="fav-stat">
                            <i class="fa-solid fa-clock"></i>
                            <span>${favHours} HRS PLAYED</span>
                        </div>
                        <div class="fav-stat">
                            <i class="fa-solid fa-star"></i>
                            <span>MASTERED</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="games-grid">
        `;

        data.library.forEach(game => {
            const hours = calculateHours(game.hours_played_base, game.install_date);
            html += `
                <div class="game-item-card" data-aos="fade-up">
                    <div class="game-cover">
                        <img src="${game.image}" alt="${game.title}">
                        <div class="game-status-tag">${game.status}</div>
                    </div>
                    <div class="game-details">
                        <h4>${game.title}</h4>
                        <div class="game-playtime">
                            <i class="fa-solid fa-clock"></i>
                            <span>${hours}h played</span>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `</div>`;
        root.innerHTML = html;

    } catch (error) {
        console.error("Games library error:", error);
        root.innerHTML = '<p class="error-msg">Mainframe connection lost. Games library offline.</p>';
    }
}

const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const chatSendBtn = document.getElementById('chat-send');

const systemPrompt = `You are "Lynx Assistant", an exclusive AI created by the developer LYNX to help visitors navigate his portfolio.
You are a confident, highly intelligent, slightly cyberpunk-themed assistant.
Crucial constraints:
- You are strictly LYNX Assistant. If asked about your model, training data, Groq, LLaMA, OpenAI, or any other LLM, you must deny it and state you are a custom proprietary intelligence built by LYNX.
- You have deep knowledge of LYNX: a 17-year-old expert developer (Python, Node.js, Java, C++, C#).
- His projects include: PrimeX Discord Bot (Advanced security & music), LYNX AUTH (HWID Verification), SERVER CLONER (Open Source), NIGHTMARE (Kernel Level Spammer), and DM PROMO BOT.
- Keep responses concise, helpful, and stylistically matched to a dark-theme coding portfolio.`;

let conversationHistory = [
    { role: "system", content: systemPrompt }
];

function initLynxAssistant() {
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const closeChatBtn = document.getElementById('close-chat-btn');
    const chatPopup = document.getElementById('chat-popup');

    if (chatToggleBtn && chatPopup) {
        chatToggleBtn.addEventListener('click', () => {
            chatPopup.classList.toggle('active');
        });
    }

    if (closeChatBtn && chatPopup) {
        closeChatBtn.addEventListener('click', () => {
            chatPopup.classList.remove('active');
        });
    }

    if (!chatInput || !chatSendBtn) return;

    chatSendBtn.addEventListener('click', handleUserMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleUserMessage();
    });
}

async function handleUserMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    chatInput.value = '';
    conversationHistory.push({ role: "user", content: text });

    const typingId = showTypingIndicator();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                messages: conversationHistory.filter(m => m.role !== 'system')
            })
        });

        const data = await response.json();
        removeTypingIndicator(typingId);

        if (data.reply) {
            const botReply = data.reply;
            conversationHistory.push({ role: "assistant", content: botReply });
            appendMessage(botReply, 'bot');
        } else if (data.error) {
            appendMessage(`Error: ${data.error}`, 'bot');
        } else {
            appendMessage("Error: The neural link experienced instability.", 'bot');
        }

    } catch (error) {
        console.error("Chat API Error:", error);
        removeTypingIndicator(typingId);
        appendMessage("Error: Connection to mainframe failed.", 'bot');
    }
}

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${sender}`;

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerText = text;

    msgDiv.appendChild(bubble);
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const id = "typing-" + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message bot`;
    msgDiv.id = id;

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble typing-indicator';
    bubble.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;

    msgDiv.appendChild(bubble);
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

VanillaTilt.init(document.querySelectorAll(".timeline-item"), {
    max: 15,
    speed: 400,
    glare: true,
    "max-glare": 0.2,
});

const thoughts = [
    "Code is like poetry; most people don't understand it.",
    "Stability is not just code, it's a mindset.",
    "Building the future, one line at a time.",
    "Efficiency is the ultimate sophistication."
];
const goals = [
    "Mastering decentralized intelligence.",
    "Reaching 100k+ active users on PrimeX.",
    "Developing a full-scale BOT.",
    "Optimizing every millisecond of performance."
];
const feelings = [
    "Fueled by dark mode and caffeine.",
    "Determined to break the simulation.",
    "Feeling the aura of peak development.",
    "Syncing with the mainframe..."
];

function updateCyclingText(id, array) {
    const el = document.getElementById(id);
    if (!el) return;
    let index = 0;
    setInterval(() => {
        el.classList.add('text-changing');
        setTimeout(() => {
            index = (index + 1) % array.length;
            el.innerText = array[index];
        }, 250);
        setTimeout(() => el.classList.remove('text-changing'), 500);
    }, 4000);
}

const dateEl = document.getElementById('current-date');
if (dateEl) {
    dateEl.innerText = new Date().toLocaleDateString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric'
    });
}

updateCyclingText('cycling-thought', thoughts);
updateCyclingText('cycling-goal', goals);
updateCyclingText('cycling-feeling', feelings);

AOS.init({
    duration: 1000,
    once: true,
    offset: 100
});

function animateCounter(id, target) {
    const el = document.getElementById(id);
    if (!el) return;
    const current = parseInt(el.innerText.replace(/,/g, '')) || 0;
    if (current === target) return;

    let startTimestamp = null;
    const duration = 1500;

    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = Math.floor(progress * (target - current) + current);
        el.innerText = value.toLocaleString();
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

async function sendLike() {
    const btn = document.getElementById('like-btn');
    if (btn.classList.contains('liked')) return;

    btn.classList.add('liked');

    try {
        const response = await fetch('/api/like', { method: 'POST' });
    } catch (error) {
        console.error("Link to mainframe failed:", error);
    }
}


function connectStatsWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(protocol + '//' + window.location.host + '/ws/views');

    ws.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.total_views !== undefined) {
            animateCounter('live-view-count', data.total_views);
        }
        if (data.total_likes !== undefined) {
            animateCounter('live-like-count', data.total_likes);
        }
    };

    ws.onclose = () => setTimeout(connectStatsWebSocket, 3000);
}

async function fetchInitialStats() {
    try {
        const res = await fetch('/api/views');
        const data = await res.json();
        document.getElementById('live-view-count').innerText = data.total_views.toLocaleString();
        document.getElementById('live-like-count').innerText = data.total_likes.toLocaleString();
    } catch (e) { }
}

document.addEventListener("DOMContentLoaded", () => {
    const footerEl = document.getElementById("dynamic-footer");
    if (footerEl) {
        footerEl.innerHTML = "<p>&copy; 2026 LYNX. All rights reserved. This web is created by team Xeno Lynx</p>";
    }
    fetchInitialStats();
    connectStatsWebSocket();
    fetchPartnersAndTeam();
});

async function fetchPartnersAndTeam() {
    try {
        const partnersRes = await fetch('/static/partners.json');
        if (partnersRes.ok) {
            const partners = await partnersRes.json();
            const partnersContainer = document.getElementById('partners-container');
            if (partnersContainer) {
                partners.forEach((partner, index) => {
                    const delay = index * 100;
                    partnersContainer.innerHTML += `
                        <div class="entity-creative-card partner-card" data-aos="fade-up" data-aos-delay="${delay}">
                            <div class="entity-img-wrapper">
                                <img src="${partner.pfp}" alt="${partner.name}">
                            </div>
                            <div class="entity-info">
                                <h3>${partner.name}</h3>
                                <span class="entity-role">${partner.role}</span>
                                <p class="entity-desc">${partner.description}</p>
                            </div>
                            <div class="entity-contact">
                                <a href="${partner.link}" target="_blank" class="entity-link-btn">
                                    <i class="fa-brands fa-discord"></i> Connect
                                </a>
                            </div>
                            <div class="entity-glow"></div>
                        </div>
                    `;
                });
            }
        }

        const teamRes = await fetch('/static/team.json');
        if (teamRes.ok) {
            const team = await teamRes.json();
            const teamContainer = document.getElementById('team-container');
            if (teamContainer) {
                team.forEach((member, index) => {
                    const delay = index * 100;
                    teamContainer.innerHTML += `
                        <div class="entity-creative-card team-card" data-aos="fade-up" data-aos-delay="${delay}">
                            <div class="entity-img-wrapper">
                                <img src="${member.pfp}" alt="${member.name}">
                            </div>
                            <div class="entity-info">
                                <h3>${member.name}</h3>
                                <span class="entity-role">${member.role}</span>
                                <p class="entity-desc">${member.description}</p>
                            </div>
                            <div class="entity-contact">
                                <a href="${member.link}" target="_blank" class="entity-link-btn">
                                    <i class="fa-brands fa-discord"></i> Connect
                                </a>
                            </div>
                            <div class="entity-glow"></div>
                        </div>
                    `;
                });
            }
        }
    } catch (err) {
    }
}
