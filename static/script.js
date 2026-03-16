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
    setInterval(fetchDiscordStatus, 60000);
    initLynxAssistant();
    initMusicPlayer();
    initCustomCursor();
    fetchInitialStats();
    connectStatsWebSocket();

    const footerEl = document.getElementById("dynamic-footer");
    if (footerEl) {
        footerEl.innerHTML = "<p>&copy; 2026 LYNX. All rights reserved. This source is created on lynxmodz.qzz.io OPEN SOURCE , by team Xeno</p>";
    }
});
