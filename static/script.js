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
        const response = await fetch('/Reviws.json');
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
});

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
