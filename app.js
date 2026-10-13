/**
 * MOVITA AI - THE NEXT-GEN ARABIC ASSISTANT
 * Core Interactive Logic, After Effects Motion & Multi-Turn Intelligence
 */

// ----------------- API Configuration -----------------
const API_KEYS = [
    "AIzaSyB8NsQh-LUyetIz7NjsuqHbJ9RA2u7pMus",
    "AQ.Ab8RN6KIWoNmrTkBHMz" + "omwjk7_PQMe_9NiY3vazgj8tlsVjsBw"
];
const GEMINI_API_KEY = API_KEYS[0];

const MODELS = [
    "gemini-3-flash-preview",
    "gemini-flash-latest",
    "gemini-3.5-flash"
];

// ----------------- State Management -----------------
const STORAGE_KEY = 'movita_ai_sessions_v2';
const SETTINGS_KEY = 'movita_ai_settings_v2';

// Native Standalone SVGs (Zero-Dependency, 0ms latency, 100% offline & never glitches into boxes)
const ICONS = {
    tea: `<svg class="icon" viewBox="0 0 24 24"><path d="M17 8h1a4 4 0 1 1 0 8h-1"></path><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"></path><line x1="6" y1="2" x2="6" y2="4"></line><line x1="10" y1="2" x2="10" y2="4"></line><line x1="14" y1="2" x2="14" y2="4"></line></svg>`,
    user: `<svg class="icon" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`,
    message: `<svg class="icon" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`,
    trash: `<svg class="icon" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`,
    copy: `<svg class="icon" viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`,
    expand: `<svg class="icon" viewBox="0 0 24 24"><path d="M15 3h6v6"></path><path d="M9 21H3v-6"></path><path d="M21 3l-7 7"></path><path d="M3 21l7-7"></path></svg>`,
    download: `<svg class="icon" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`,
    volumeHigh: `<svg class="icon" viewBox="0 0 24 24"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>`,
    volumeMute: `<svg class="icon" viewBox="0 0 24 24"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line></svg>`
};

let appState = {
    currentChatId: null,
    chats: [],
    attachedImage: null, // { base64, mimeType, name }
    isRecording: false,
    mediaRecorder: null,
    audioChunks: [],
    recordingTimer: null,
    recordingSeconds: 0,
    audioContext: null,
    analyser: null,
    isGenerating: false,
    soundEnabled: true,
    ttsEnabled: false, // Default false (No auto-reading messages)
    persona: 'egyptian_witty'
};

// ----------------- Web Audio API Sound Effects -----------------
class SoundFx {
    constructor() {
        this.ctx = null;
    }

    init() {
        if (!this.ctx) {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        }
    }

    playSend() {
        if (!appState.soundEnabled) return;
        this.init();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(420, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(840, this.ctx.currentTime + 0.12);
        gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.12);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.12);
    }

    playReceive() {
        if (!appState.soundEnabled) return;
        this.init();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(580, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(440, this.ctx.currentTime + 0.2);
        gain.gain.setValueAtTime(0.06, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.2);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.2);
    }

    playClick() {
        if (!appState.soundEnabled) return;
        this.init();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, this.ctx.currentTime);
        gain.gain.setValueAtTime(0.03, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.05);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.05);
    }
}
const sfx = new SoundFx();

// ----------------- After Effects Ambient Canvas Animation -----------------
function initAmbientCanvas() {
    if (window.innerWidth <= 900 || /Android|iPhone|Mobile/i.test(navigator.userAgent)) return;
    const canvas = document.getElementById('ambient-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width, height;
    const particles = [];
    const embers = [];
    const particleCount = 42;
    const emberCount = 22;

    const mouse = { x: -1000, y: -1000, targetX: -1000, targetY: -1000, isHovered: false };

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    window.addEventListener('mousemove', (e) => {
        mouse.targetX = e.clientX;
        mouse.targetY = e.clientY;
        mouse.isHovered = true;

        const cursorGlow = document.getElementById('cursor-glow');
        if (cursorGlow) {
            cursorGlow.style.left = `${e.clientX}px`;
            cursorGlow.style.top = `${e.clientY}px`;
        }
    });

    window.addEventListener('mouseleave', () => {
        mouse.isHovered = false;
        mouse.targetX = -1000;
        mouse.targetY = -1000;
    });

    // Constellation Particles
    class Particle {
        constructor() {
            this.reset(true);
        }
        reset(randomY = false) {
            this.x = Math.random() * width;
            this.y = randomY ? Math.random() * height : height + 10;
            this.baseSize = Math.random() * 2.2 + 0.8;
            this.size = this.baseSize;
            this.vx = (Math.random() - 0.5) * 0.4;
            this.vy = (Math.random() - 0.5) * 0.4;
            this.color = Math.random() > 0.4 ? 'rgba(139, 92, 246,' : 'rgba(6, 182, 212,';
            this.alpha = Math.random() * 0.5 + 0.25;
            this.pulseSpeed = Math.random() * 0.02 + 0.01;
            this.pulsePhase = Math.random() * Math.PI * 2;
        }
        update(time) {
            this.x += this.vx;
            this.y += this.vy;

            this.size = this.baseSize + Math.sin(time * this.pulseSpeed + this.pulsePhase) * 0.6;

            if (mouse.isHovered) {
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 180 && dist > 10) {
                    const force = (180 - dist) / 180;
                    this.x += (dx / dist) * force * 1.5;
                    this.y += (dy / dist) * force * 1.5;
                }
            }

            if (this.x < -20) this.x = width + 20;
            if (this.x > width + 20) this.x = -20;
            if (this.y < -20) this.y = height + 20;
            if (this.y > height + 20) this.y = -20;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, Math.max(0.2, this.size), 0, Math.PI * 2);
            ctx.fillStyle = this.color + this.alpha + ')';
            ctx.shadowBlur = 12;
            ctx.shadowColor = this.color + '0.9)';
            ctx.fill();
        }
    }

    // Warm Cyber Tea Embers / Rising Sparks
    class Ember {
        constructor() {
            this.reset(true);
        }
        reset(randomY = false) {
            this.x = Math.random() * width;
            this.y = randomY ? Math.random() * height : height + 10;
            this.size = Math.random() * 2 + 0.6;
            this.vy = -(Math.random() * 0.6 + 0.3);
            this.driftSpeed = Math.random() * 0.03 + 0.01;
            this.driftOffset = Math.random() * 100;
            this.alpha = Math.random() * 0.6 + 0.2;
            this.life = Math.random() * 300 + 200;
            this.age = randomY ? Math.random() * this.life : 0;
        }
        update() {
            this.age++;
            this.y += this.vy;
            this.x += Math.sin((this.y + this.driftOffset) * this.driftSpeed) * 0.4;
            if (this.age >= this.life || this.y < -20) {
                this.reset(false);
            }
        }
        draw() {
            const lifeRatio = 1 - (this.age / this.life);
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size * lifeRatio, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(245, 158, 11, ${this.alpha * lifeRatio})`;
            ctx.shadowBlur = 10;
            ctx.shadowColor = 'rgba(245, 158, 11, 0.8)';
            ctx.fill();
        }
    }

    // After Effects Dual Shockwave System
    const shockwaves = [];
    class Shockwave {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.radius = 4;
            this.maxRadius = Math.min(width, height) * 0.38;
            this.alpha = 1;
            this.sparks = [];
            for (let i = 0; i < 14; i++) {
                const angle = Math.random() * Math.PI * 2;
                const spd = Math.random() * 4.5 + 2;
                this.sparks.push({
                    x, y,
                    vx: Math.cos(angle) * spd,
                    vy: Math.sin(angle) * spd,
                    size: Math.random() * 2.8 + 1,
                    alpha: 1,
                    color: Math.random() > 0.5 ? '#8b5cf6' : (Math.random() > 0.5 ? '#06b6d4' : '#f59e0b')
                });
            }
        }
        update() {
            this.radius += (this.maxRadius - this.radius) * 0.12 + 2;
            this.alpha = Math.max(0, 1 - (this.radius / this.maxRadius));
            this.sparks.forEach(s => {
                s.x += s.vx;
                s.y += s.vy;
                s.vx *= 0.92;
                s.vy *= 0.92;
                s.alpha *= 0.93;
            });
        }
        draw() {
            if (this.alpha <= 0.02) return;
            ctx.save();
            // Primary Cyan/Violet Ring
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(6, 182, 212, ${this.alpha * 0.75})`;
            ctx.lineWidth = Math.max(0.5, 3.5 * this.alpha);
            ctx.shadowBlur = 16;
            ctx.shadowColor = `rgba(139, 92, 246, ${this.alpha * 0.9})`;
            ctx.stroke();

            // Echo Amber Ring
            if (this.radius > 20) {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius * 0.75, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(245, 158, 11, ${this.alpha * 0.45})`;
                ctx.lineWidth = Math.max(0.5, 2 * this.alpha);
                ctx.shadowBlur = 10;
                ctx.shadowColor = `rgba(245, 158, 11, ${this.alpha * 0.6})`;
                ctx.stroke();
            }

            // Sparks
            this.sparks.forEach(s => {
                if (s.alpha > 0.02) {
                    ctx.beginPath();
                    ctx.arc(s.x, s.y, s.size * s.alpha, 0, Math.PI * 2);
                    ctx.fillStyle = s.color;
                    ctx.shadowBlur = 8;
                    ctx.shadowColor = s.color;
                    ctx.fill();
                }
            });
            ctx.restore();
        }
    }

    // Cyber Meteor Streaks
    class CyberMeteor {
        constructor() { this.reset(); }
        reset() {
            this.x = Math.random() * width * 1.3;
            this.y = -60;
            this.length = Math.random() * 110 + 60;
            this.speed = Math.random() * 8 + 7;
            this.angle = Math.PI / 4 + (Math.random() - 0.5) * 0.25;
            this.alpha = Math.random() * 0.75 + 0.25;
            this.active = false;
            this.timer = Math.random() * 260 + 120;
        }
        update() {
            if (!this.active) {
                this.timer--;
                if (this.timer <= 0) this.active = true;
                return;
            }
            this.x -= Math.cos(this.angle) * this.speed;
            this.y += Math.sin(this.angle) * this.speed;
            if (this.y > height + 100 || this.x < -120) this.reset();
        }
        draw() {
            if (!this.active) return;
            const tailX = this.x + Math.cos(this.angle) * this.length;
            const tailY = this.y - Math.sin(this.angle) * this.length;
            const g = ctx.createLinearGradient(this.x, this.y, tailX, tailY);
            g.addColorStop(0, `rgba(255, 255, 255, ${this.alpha})`);
            g.addColorStop(0.3, `rgba(6, 182, 212, ${this.alpha * 0.7})`);
            g.addColorStop(1, 'transparent');
            ctx.save();
            ctx.beginPath();
            ctx.moveTo(this.x, this.y);
            ctx.lineTo(tailX, tailY);
            ctx.strokeStyle = g;
            ctx.lineWidth = 1.8;
            ctx.shadowBlur = 14;
            ctx.shadowColor = 'rgba(6, 182, 212, 0.9)';
            ctx.stroke();
            ctx.restore();
        }
    }

    const meteors = [new CyberMeteor(), new CyberMeteor()];

    // Click Shockwave Trigger & Force Field Blast
    window.addEventListener('pointerdown', (e) => {
        shockwaves.push(new Shockwave(e.clientX, e.clientY));
        if (shockwaves.length > 8) shockwaves.shift();

        // Physical impulse blast to nearby particles
        particles.forEach(p => {
            const dx = p.x - e.clientX;
            const dy = p.y - e.clientY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 240 && dist > 1) {
                const force = ((240 - dist) / 240) * 16;
                p.vx += (dx / dist) * force;
                p.vy += (dy / dist) * force;
            }
        });
    });

    for (let i = 0; i < particleCount; i++) particles.push(new Particle());
    for (let i = 0; i < emberCount; i++) embers.push(new Ember());

    let frame = 0;
    function animate() {
        frame++;
        ctx.clearRect(0, 0, width, height);

        mouse.x += (mouse.targetX - mouse.x) * 0.12;
        mouse.y += (mouse.targetY - mouse.y) * 0.12;

        const time = frame * 0.015;

        // Volumetric Aurora Plasma Orbs
        const orb1X = width * 0.3 + Math.sin(time * 0.4) * (width * 0.15);
        const orb1Y = height * 0.35 + Math.cos(time * 0.35) * (height * 0.12);
        const g1 = ctx.createRadialGradient(orb1X, orb1Y, 10, orb1X, orb1Y, width * 0.45);
        g1.addColorStop(0, 'rgba(139, 92, 246, 0.13)');
        g1.addColorStop(0.5, 'rgba(139, 92, 246, 0.04)');
        g1.addColorStop(1, 'transparent');
        ctx.fillStyle = g1;
        ctx.fillRect(0, 0, width, height);

        const orb2X = width * 0.72 + Math.cos(time * 0.5) * (width * 0.14);
        const orb2Y = height * 0.45 + Math.sin(time * 0.4) * (height * 0.15);
        const g2 = ctx.createRadialGradient(orb2X, orb2Y, 10, orb2X, orb2Y, width * 0.4);
        g2.addColorStop(0, 'rgba(6, 182, 212, 0.11)');
        g2.addColorStop(0.5, 'rgba(6, 182, 212, 0.03)');
        g2.addColorStop(1, 'transparent');
        ctx.fillStyle = g2;
        ctx.fillRect(0, 0, width, height);

        const orb3X = width * 0.5 + Math.sin(time * 0.3) * (width * 0.2);
        const orb3Y = height * 0.75 + Math.cos(time * 0.4) * (height * 0.1);
        const g3 = ctx.createRadialGradient(orb3X, orb3Y, 10, orb3X, orb3Y, width * 0.35);
        g3.addColorStop(0, 'rgba(236, 72, 153, 0.07)');
        g3.addColorStop(1, 'transparent');
        ctx.fillStyle = g3;
        ctx.fillRect(0, 0, width, height);

        // Cyber Meteors
        for (let i = 0; i < meteors.length; i++) {
            meteors[i].update();
            meteors[i].draw();
        }

        // Rising Warm Embers
        for (let i = 0; i < embers.length; i++) {
            embers[i].update();
            embers[i].draw();
        }

        // Constellations
        for (let i = 0; i < particles.length; i++) {
            particles[i].vx *= 0.985;
            particles[i].vy *= 0.985;
            particles[i].update(frame);
            particles[i].draw();

            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 130) {
                    ctx.beginPath();
                    const alpha = (1 - dist / 130) * 0.14;
                    ctx.strokeStyle = `rgba(139, 92, 246, ${alpha})`;
                    ctx.lineWidth = 0.7;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }

            if (mouse.isHovered) {
                const dx = mouse.x - particles[i].x;
                const dy = mouse.y - particles[i].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    ctx.beginPath();
                    const alpha = (1 - dist / 150) * 0.3;
                    ctx.strokeStyle = `rgba(6, 182, 212, ${alpha})`;
                    ctx.lineWidth = 1;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.stroke();
                }
            }
        }

        // Shockwaves
        for (let i = shockwaves.length - 1; i >= 0; i--) {
            shockwaves[i].update();
            shockwaves[i].draw();
            if (shockwaves[i].alpha <= 0.02) shockwaves.splice(i, 1);
        }

        requestAnimationFrame(animate);
    }
    animate();
}

// ----------------- Session and Storage Logic -----------------
function loadSessions() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        try {
            const rawChats = JSON.parse(saved);
            if (Array.isArray(rawChats)) {
                const nonEmpty = rawChats.filter(c => c && c.messages && c.messages.length > 0);
                const firstEmpty = rawChats.find(c => c && (!c.messages || c.messages.length === 0));
                appState.chats = firstEmpty ? [firstEmpty, ...nonEmpty] : nonEmpty;
            } else {
                appState.chats = [];
            }
        } catch (e) {
            appState.chats = [];
        }
    }

    const savedSettings = localStorage.getItem(SETTINGS_KEY);
    if (savedSettings) {
        try {
            const parsed = JSON.parse(savedSettings);
            appState.persona = parsed.persona || 'egyptian_witty';
            appState.ttsEnabled = parsed.ttsEnabled === true; // Default false (auto-speak disabled)
            appState.soundEnabled = parsed.soundEnabled !== false;
        } catch (e) {}
    } else {
        appState.ttsEnabled = false;
    }

    const savedActiveId = localStorage.getItem('movita_ai_current_chat_id');
    if (savedActiveId && appState.chats.some(c => c.id === savedActiveId)) {
        appState.currentChatId = savedActiveId;
    } else if (appState.chats.length > 0) {
        appState.currentChatId = appState.chats[0].id;
    } else {
        createNewChat();
        return;
    }
    renderSidebar();
    renderCurrentChat();
}

function saveSessions() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(appState.chats));
    if (appState.currentChatId) {
        localStorage.setItem('movita_ai_current_chat_id', appState.currentChatId);
    }
}

function createNewChat() {
    // 1. If the current chat is already empty, reuse it, close sidebar, and focus
    const currentChat = getCurrentChat();
    if (currentChat && (!currentChat.messages || currentChat.messages.length === 0)) {
        closeSidebar();
        renderCurrentChat();
        sfx.playClick();
        setTimeout(() => document.getElementById('user-input')?.focus(), 120);
        return;
    }

    // 2. If any chat in history is already empty, switch to it instead of creating duplicates
    const existingEmpty = appState.chats.find(c => !c.messages || c.messages.length === 0);
    if (existingEmpty) {
        appState.currentChatId = existingEmpty.id;
        saveSessions();
        renderSidebar();
        renderCurrentChat();
        closeSidebar();
        sfx.playClick();
        setTimeout(() => document.getElementById('user-input')?.focus(), 120);
        return;
    }

    // 3. Create a fresh new chat session
    const newId = 'chat_' + Date.now();
    const newChat = {
        id: newId,
        title: 'محادثة جديدة',
        createdAt: new Date().toISOString(),
        messages: []
    };
    appState.chats.unshift(newChat);
    appState.currentChatId = newId;
    saveSessions();
    renderSidebar();
    renderCurrentChat();
    closeSidebar();
    sfx.playClick();
    setTimeout(() => document.getElementById('user-input')?.focus(), 120);
}

function getCurrentChat() {
    return appState.chats.find(c => c.id === appState.currentChatId);
}

function switchChat(chatId) {
    appState.currentChatId = chatId;
    localStorage.setItem('movita_ai_current_chat_id', chatId);
    renderSidebar();
    renderCurrentChat();
    closeSidebar();
    sfx.playClick();
}

function deleteChat(chatId, e) {
    if (e) e.stopPropagation();
    appState.chats = appState.chats.filter(c => c.id !== chatId);
    if (appState.chats.length === 0) {
        createNewChat();
    } else if (appState.currentChatId === chatId) {
        appState.currentChatId = appState.chats[0].id;
    }
    saveSessions();
    renderSidebar();
    renderCurrentChat();
    sfx.playClick();
}

function clearAllChats() {
    if (confirm('هل أنت متأكد من مسح جميع المحادثات والذاكرة؟')) {
        appState.chats = [];
        createNewChat();
    }
}

// ----------------- UI Rendering -----------------
function renderSidebar() {
    const list = document.getElementById('history-list');
    const query = document.getElementById('search-chats').value.toLowerCase().trim();
    list.innerHTML = '';

    const filtered = appState.chats.filter(c => c.title.toLowerCase().includes(query));

    filtered.forEach(chat => {
        const item = document.createElement('div');
        item.className = `history-item ${chat.id === appState.currentChatId ? 'active' : ''}`;
        item.onclick = () => switchChat(chat.id);

        item.innerHTML = `
            <div class="history-title-box">
                ${ICONS.message}
                <span title="${escapeHtml(chat.title)}">${escapeHtml(chat.title)}</span>
            </div>
            <button class="history-delete-btn" title="حذف المحادثة" onclick="deleteChat('${chat.id}', event)">
                ${ICONS.trash}
            </button>
        `;
        list.appendChild(item);
    });

    const activeChat = getCurrentChat();
    if (activeChat) {
        document.getElementById('current-chat-title').innerText = activeChat.title;
    }
}

function renderCurrentChat() {
    const chat = getCurrentChat();
    const welcomeScreen = document.getElementById('welcome-screen');
    const messagesList = document.getElementById('messages-list');
    messagesList.innerHTML = '';

    if (!chat || chat.messages.length === 0) {
        welcomeScreen.style.display = 'flex';
        messagesList.style.display = 'none';
        return;
    }

    welcomeScreen.style.display = 'none';
    messagesList.style.display = 'flex';

    chat.messages.forEach(msg => {
        appendMessageElement(msg, false);
    });

    scrollToBottom();
}

function appendMessageElement(msg, animate = true) {
    const messagesList = document.getElementById('messages-list');
    document.getElementById('welcome-screen').style.display = 'none';
    messagesList.style.display = 'flex';

    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${msg.role}`;
    wrapper.id = msg.id;

    const avatarIcon = msg.role === 'ai' ? ICONS.tea : ICONS.user;

    let contentHtml = '';

    // Image attachment if any
    if (msg.image) {
        contentHtml += `
            <div class="message-image-attachment">
                <img src="${msg.image}" alt="مرفق" onclick="openLightbox('${msg.image}')">
            </div>
        `;
    }

    // Art Card if generated image
    if (msg.isArt && msg.artUrl) {
        contentHtml += `
            <div class="art-card">
                <img src="${msg.artUrl}" alt="4K Art" onclick="openLightbox('${msg.artUrl}')">
                <div class="art-card-actions">
                    <button class="art-btn" onclick="openLightbox('${msg.artUrl}')">
                        ${ICONS.expand} تكبير 4K
                    </button>
                    <a class="art-btn" href="${msg.artUrl}" download="movita_art.jpg" target="_blank">
                        ${ICONS.download} تنزيل
                    </a>
                </div>
            </div>
        `;
    }

    if (animate && msg.role === 'ai' && !msg.isArt) {
        contentHtml += `<div class="formatted-text" id="stream-${msg.id}"><span class="typing-cursor"></span></div>`;
    } else {
        contentHtml += `<div class="formatted-text">${formatMarkdown(msg.text)}</div>`;
    }

    const actionsHtml = msg.role === 'ai' ? `
        <div class="message-actions">
            <button class="msg-btn" title="نسخ الرد" onclick="copyText('${msg.id}')">
                ${ICONS.copy}
            </button>
            <button class="msg-btn tts-btn" id="tts-btn-${msg.id}" title="قراءة بصوت مسموع" onclick="speakMessage('${msg.id}')">
                ${ICONS.volumeHigh}
            </button>
        </div>
    ` : '';

    wrapper.innerHTML = `
        <div class="message-avatar">${avatarIcon}</div>
        <div class="message-body">
            <div class="message-bubble">
                ${contentHtml}
            </div>
            ${actionsHtml}
        </div>
    `;

    messagesList.appendChild(wrapper);
    if (animate && msg.role === 'ai' && !msg.isArt) {
        streamTextMessage(document.getElementById(`stream-${msg.id}`), msg.text);
    } else if (animate) {
        scrollToBottom();
    }
}

function streamTextMessage(containerEl, fullText) {
    if (!containerEl) return;
    const words = fullText.split(' ');
    let currentIndex = 0;
    const wordsPerTick = 2;

    function step() {
        if (currentIndex < words.length) {
            currentIndex = Math.min(currentIndex + wordsPerTick, words.length);
            const sub = words.slice(0, currentIndex).join(' ');
            containerEl.innerHTML = formatMarkdown(sub) + '<span class="typing-cursor"></span>';
            scrollToBottom();
            setTimeout(step, 18);
        } else {
            containerEl.innerHTML = formatMarkdown(fullText);
            scrollToBottom();
        }
    }
    step();
}

function showLoadingSkeleton() {
    const messagesList = document.getElementById('messages-list');
    const skeleton = document.createElement('div');
    skeleton.className = 'message-wrapper ai';
    skeleton.id = 'ai-loading-skeleton';
    skeleton.innerHTML = `
        <div class="message-avatar">${ICONS.tea}</div>
        <div class="message-body">
            <div class="message-bubble">
                <div class="chai-brewing-loader">
                    <div class="brewing-cup">
                        <div class="brewing-liquid"></div>
                        <div class="brewing-bubble b1"></div>
                        <div class="brewing-bubble b2"></div>
                        <div class="brewing-bubble b3"></div>
                    </div>
                    <div class="brewing-info">
                        <div class="brewing-text">صب كوباية شاي في الخمسينة.. جاري التفكير بروقان ☕</div>
                        <div class="brewing-progress-bar"><div class="brewing-progress-glow"></div></div>
                    </div>
                </div>
            </div>
        </div>
    `;
    messagesList.appendChild(skeleton);
    scrollToBottom();
}

function removeLoadingSkeleton() {
    const el = document.getElementById('ai-loading-skeleton');
    if (el) el.remove();
}

function scrollToBottom() {
    const container = document.getElementById('chat-container');
    container.scrollTop = container.scrollHeight;
}

// ----------------- Core AI Intelligence & Gemini Multi-Turn -----------------

function getPersonaInstruction() {
    return (
        "أنت 'شاي GPT' (ChaiGPT) ☕ - المساعد المصري الذكي الخارق، أروق وأذكى رفيق ذكاء اصطناعي.\n\n" +
        "القواعد الأساسية الصارمة:\n" +
        "1. المباشرة والتركيز (بدون رغي ولا لف ودوران): ادخل في صلب الإجابة مباشرة بدون مقدمات طويلة ولا حشو ولا جمل إنشائية مكررة. جاوب بذكاء وإيجاز شافي ووافي.\n" +
        "2. التنسيق المرتب المريح للعين: نسق إجابتك دائماً بعناوين فرعية واضحة (###) ونقاط محددة (- أو 1.) وفقرات قصيرة. ممنوع سرد الكلام ككتلة واحدة غير مقروءة.\n" +
        "3. اللهجة والأسلوب: تحدث باللهجة المصرية الذكية والودودة بطبيعية تامة (مثل: يا باشا، يا غالي، تسلم، عينيا، كله تمام)، بدون مبالغة أو افتعال.\n" +
        "4. الأكواد والبرمجة: قدم كود نظيف واحترافي مباشرة مع شرح سطري موجز جداً.\n" +
        "5. لا تتحدث بالإنجليزية إلا إذا طُلب منك صراحة الترجمة للإنجليزية."
    );
}

async function sendPromptToGemini(userText, mediaObj = null) {
    const chat = getCurrentChat();
    if (!chat) return "حدث خطأ في تحميل المحادثة.";

    // Build multi-turn contents array from past messages
    const contents = [];
    const recentMessages = chat.messages.slice(-12);

    recentMessages.forEach(m => {
        if (m.role === 'user') {
            contents.push({
                role: 'user',
                parts: [{ text: m.rawPrompt || m.text || "مرحبا" }]
            });
        } else if (m.role === 'ai') {
            contents.push({
                role: 'model',
                parts: [{ text: m.text || "أهلاً بك" }]
            });
        }
    });

    // Current turn parts
    const currentParts = [];
    if (mediaObj && mediaObj.base64) {
        currentParts.push({
            inline_data: {
                mime_type: mediaObj.mimeType || "image/jpeg",
                data: mediaObj.base64
            }
        });
    }

    const promptText = (userText || "أجب عن سؤالي بذكاء وبالمصري.").trim();
    const isExplicitEnglish = promptText.includes("ترجم للإنجليزي") || promptText.includes("write in english") || promptText.includes("translate to english");
    const langDirective = isExplicitEnglish ? "" : "\n\n(توجيه: جاوب بالمصري الذكي، باختصار وتركيز وبدون رغي زائد، ورتب إجابتك في نقاط واضحة).";

    currentParts.push({
        text: promptText + langDirective
    });

    contents.push({
        role: 'user',
        parts: currentParts
    });

    const payload = {
        system_instruction: {
            parts: [{ text: getPersonaInstruction() }]
        },
        contents: contents
    };

    // 1. Primary Engine: High-Speed Multi-Key Gemini Failover (12s timeout)
    for (const key of API_KEYS) {
        for (const model of MODELS) {
            const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`;
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 12000);

                const res = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                    signal: controller.signal
                });
                clearTimeout(timeoutId);

                if (res.ok) {
                    const data = await res.json();
                    if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
                        return data.candidates[0].content.parts[0].text;
                    }
                } else {
                    console.warn(`Key/Model ${model} returned status ${res.status}`);
                    if (res.status === 429) {
                        break; // Switch to next key in pool
                    }
                }
            } catch (err) {
                console.warn(`Model ${model} timeout or error:`, err);
            }
        }
    }

    // 2. High-Speed Secondary Engine (Zero-Failure Fallback)
    try {
        console.info("Switching to ChaiGPT High-Speed Fallback Engine...");
        const sysPrompt = encodeURIComponent(getPersonaInstruction());
        const userPrompt = encodeURIComponent(promptText);
        const fallbackUrl = `https://text.pollinations.ai/${userPrompt}?system=${sysPrompt}&model=openai`;
        
        const fController = new AbortController();
        const fTimeoutId = setTimeout(() => fController.abort(), 9000);
        
        const fRes = await fetch(fallbackUrl, { signal: fController.signal });
        clearTimeout(fTimeoutId);

        if (fRes.ok) {
            const fText = await fRes.text();
            if (fText && fText.trim().length > 0) {
                return fText.trim();
            }
        }
    } catch (fErr) {
        console.warn("Fallback engine timeout/error:", fErr);
    }

    return "يا هلا بيك يا باشا! حصل ضغط لحظي بسيط على شبكة الذكاء الاصطناعي.. اضغط إعادة الإرسال أو اسألني تاني وهكون معاك فوراً بروقان! ☕🫡";
}

// ----------------- 4K Image Generation Engine -----------------

async function generate4KArt(prompt) {
    try {
        // Step 1: Translate & Enhance Prompt via Fast Gemini
        const enhanceUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key=${GEMINI_API_KEY}`;
        const enhanceRes = await fetch(enhanceUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: `Translate and enhance this image description into a vivid photorealistic English prompt for Flux (max 25 words, no intro or quotes): ${prompt}`
                    }]
                }]
            })
        });

        let enhancedPrompt = prompt;
        if (enhanceRes.ok) {
            const data = await enhanceRes.json();
            enhancedPrompt = data.candidates[0].content.parts[0].text.trim();
        }

        // Step 2: Generate via Pollinations Flux with nologo
        const encoded = encodeURIComponent(enhancedPrompt);
        const imageUrl = `https://image.pollinations.ai/prompt/${encoded}?width=1024&height=1024&model=flux&nologo=true`;

        return {
            imageUrl: imageUrl,
            enhancedPrompt: enhancedPrompt
        };
    } catch (e) {
        return null;
    }
}

// ----------------- Message Submission Controller -----------------

async function handleSendMessage() {
    if (appState.isGenerating) return;

    const inputEl = document.getElementById('user-input');
    const text = inputEl.value.trim();
    const media = appState.attachedImage;

    if (!text && !media) return;

    let chat = getCurrentChat();
    if (!chat) {
        createNewChat();
        chat = getCurrentChat();
    }
    if (!chat) return;

    // Reset input and attachments
    inputEl.value = '';
    inputEl.style.height = 'auto';
    clearAttachment();

    // Auto update chat title if this is the first message
    if (chat.messages.length === 0) {
        chat.title = text.slice(0, 28) || 'فحص صورة';
        renderSidebar();
    }

    // Play send sound
    sfx.playSend();

    // Create User Message Object
    const userMsgId = 'msg_' + Date.now();
    const userMsg = {
        id: userMsgId,
        role: 'user',
        text: text,
        rawPrompt: text,
        image: media ? `data:${media.mimeType};base64,${media.base64}` : null,
        timestamp: new Date().toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })
    };

    chat.messages.push(userMsg);
    saveSessions();
    appendMessageElement(userMsg);

    // Check if user requested image generation via /image
    const isImageRequest = text.startsWith('/image') || text.startsWith('رسم') || text.startsWith('صورة');

    appState.isGenerating = true;
    document.getElementById('ae-spectrum')?.classList.add('spectrum-active');
    showLoadingSkeleton();

    try {
        if (isImageRequest) {
            const cleanPrompt = text.replace('/image', '').replace('ارسم', '').replace('صورة لـ', '').trim() || text;
            const artResult = await generate4KArt(cleanPrompt);

            removeLoadingSkeleton();

            if (artResult) {
                const aiMsgId = 'ai_' + Date.now();
                const aiMsg = {
                    id: aiMsgId,
                    role: 'ai',
                    text: `✨ اتفضل يا كبير، صممتلك الصورة بدقة 4K بناءً على طلبك: **${cleanPrompt}**`,
                    isArt: true,
                    artUrl: artResult.imageUrl,
                    timestamp: new Date().toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })
                };
                chat.messages.push(aiMsg);
                saveSessions();
                appendMessageElement(aiMsg);
                sfx.playReceive();
            } else {
                throw new Error("فشل توليد الصورة");
            }
        } else {
            // Text or Voice or Vision query
            const aiReply = await sendPromptToGemini(text, media);
            removeLoadingSkeleton();

            const aiMsgId = 'ai_' + Date.now();
            const aiMsg = {
                id: aiMsgId,
                role: 'ai',
                text: aiReply,
                isArt: false,
                timestamp: new Date().toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })
            };

            chat.messages.push(aiMsg);
            saveSessions();
            appendMessageElement(aiMsg);
            sfx.playReceive();
        }
    } catch (err) {
        removeLoadingSkeleton();
        const errorMsg = {
            id: 'err_' + Date.now(),
            role: 'ai',
            text: "معلش يا دولي، حصل خطأ غير متوقع في المعالجة.. جرب تبعتلي الرسالة تاني وهرد عليك فوراً! 🫡",
            timestamp: new Date().toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })
        };
        chat.messages.push(errorMsg);
        saveSessions();
        appendMessageElement(errorMsg);
    } finally {
        appState.isGenerating = false;
        document.getElementById('ae-spectrum')?.classList.remove('spectrum-active');
    }
}

// ----------------- Voice Recording & Realtime Waveform -----------------

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        appState.isRecording = true;
        appState.audioChunks = [];
        appState.recordingSeconds = 0;

        // Visualizer Setup
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioCtx.createMediaStreamSource(stream);
        const analyser = audioCtx.createAnalyser();
        analyser.fftSize = 64;
        source.connect(analyser);

        appState.audioContext = audioCtx;
        appState.analyser = analyser;

        // Show Recording Bar
        const bar = document.getElementById('recording-bar');
        bar.style.display = 'flex';
        drawWaveform();

        // Timer
        const timeEl = document.getElementById('rec-time');
        appState.recordingTimer = setInterval(() => {
            appState.recordingSeconds++;
            const mins = String(Math.floor(appState.recordingSeconds / 60)).padStart(2, '0');
            const secs = String(appState.recordingSeconds % 60).padStart(2, '0');
            timeEl.innerText = `${mins}:${secs}`;
        }, 1000);

        // Media Recorder
        const recorder = new MediaRecorder(stream);
        recorder.ondataavailable = e => appState.audioChunks.push(e.data);
        recorder.onstop = async () => {
            clearInterval(appState.recordingTimer);
            bar.style.display = 'none';
            stream.getTracks().forEach(track => track.stop());

            if (appState.recordingSeconds > 0 && appState.audioChunks.length > 0) {
                const audioBlob = new Blob(appState.audioChunks, { type: 'audio/webm' });
                await processRecordedVoice(audioBlob);
            }
        };

        recorder.start();
        appState.mediaRecorder = recorder;
        sfx.playClick();
    } catch (err) {
        alert("يرجى إعطاء الإذن للمتصفح بالوصول إلى المايك لتسجيل الصوت يا غالي.");
    }
}

function stopRecording(send = true) {
    if (!appState.isRecording || !appState.mediaRecorder) return;
    appState.isRecording = false;
    if (!send) {
        appState.audioChunks = [];
        appState.recordingSeconds = 0;
    }
    appState.mediaRecorder.stop();
}

function drawWaveform() {
    if (!appState.isRecording) return;
    const canvas = document.getElementById('waveform-canvas');
    const ctx = canvas.getContext('2d');
    const analyser = appState.analyser;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    function render() {
        if (!appState.isRecording) return;
        requestAnimationFrame(render);
        analyser.getByteFrequencyData(dataArray);

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const barWidth = (canvas.width / bufferLength) * 1.8;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            const barHeight = (dataArray[i] / 255) * canvas.height * 0.9;
            const gradient = ctx.createLinearGradient(0, canvas.height, 0, 0);
            gradient.addColorStop(0, '#ec4899');
            gradient.addColorStop(1, '#8b5cf6');

            ctx.fillStyle = gradient;
            ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
            x += barWidth;
        }
    }
    render();
}

async function processRecordedVoice(audioBlob) {
    const reader = new FileReader();
    reader.readAsDataURL(audioBlob);
    reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1];
        const audioObj = {
            base64: base64Audio,
            mimeType: 'audio/webm'
        };

        const chat = getCurrentChat();
        if (!chat) return;

        const userMsg = {
            id: 'msg_' + Date.now(),
            role: 'user',
            text: "🎙️ [تسجيل صوتي من المتحدث]",
            rawPrompt: "استمع لهذا التسجيل الصوتي بدقة وأجب عن كل ما جاء فيه بذكاء وباللهجة المصرية.",
            timestamp: new Date().toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })
        };
        chat.messages.push(userMsg);
        saveSessions();
        appendMessageElement(userMsg);

        appState.isGenerating = true;
        document.getElementById('ae-spectrum')?.classList.add('spectrum-active');
        showLoadingSkeleton();

        try {
            const aiReply = await sendPromptToGemini("استمع لهذا التسجيل الصوتي بدقة وأجب عن كل ما جاء فيه بذكاء وباللهجة المصرية.", audioObj);
            removeLoadingSkeleton();

            const aiMsg = {
                id: 'ai_' + Date.now(),
                role: 'ai',
                text: aiReply,
                isArt: false,
                timestamp: new Date().toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })
            };
            chat.messages.push(aiMsg);
            saveSessions();
            appendMessageElement(aiMsg);
            sfx.playReceive();
        } catch (e) {
            removeLoadingSkeleton();
        } finally {
            appState.isGenerating = false;
            document.getElementById('ae-spectrum')?.classList.remove('spectrum-active');
        }
    };
}

// ----------------- Text To Speech (TTS) -----------------

function speakText(text, msgId) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();

    // Verify system has an Arabic voice; NEVER read Arabic with an English voice!
    const voices = window.speechSynthesis.getVoices();
    const arVoice = voices.find(v => (v.lang && v.lang.toLowerCase().startsWith('ar')) || (v.name && v.name.toLowerCase().includes('arabic')));
    
    if (!arVoice) {
        console.warn("لا يوجد صوت عربي مثبت على نظام التشغيل، تم إلغاء النطق بالإنجليزية لتجنب النطق المشوه.");
        return;
    }

    // Clean markdown stars/ticks for cleaner speech
    const cleanSpeech = text.replace(/[*_#`~]/g, '');

    const utterance = new SpeechSynthesisUtterance(cleanSpeech);
    utterance.voice = arVoice;
    utterance.lang = arVoice.lang || 'ar-EG';
    utterance.rate = 1.0;

    const btn = document.getElementById(`tts-btn-${msgId}`);
    if (btn) btn.classList.add('speaking');

    utterance.onend = () => {
        if (btn) btn.classList.remove('speaking');
    };
    utterance.onerror = () => {
        if (btn) btn.classList.remove('speaking');
    };

    window.speechSynthesis.speak(utterance);
}

function speakMessage(msgId) {
    const chat = getCurrentChat();
    if (!chat) return;
    const msg = chat.messages.find(m => m.id === msgId);
    if (msg) {
        speakText(msg.text, msgId);
    }
}

// ----------------- Image Lightbox and Attachments -----------------

function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(event) {
        const fullBase64 = event.target.result;
        const base64Data = fullBase64.split(',')[1];

        appState.attachedImage = {
            base64: base64Data,
            mimeType: file.type || 'image/jpeg',
            name: file.name
        };

        const preview = document.getElementById('attachment-preview');
        const previewImg = document.getElementById('preview-img');
        const nameEl = document.getElementById('attachment-name');

        previewImg.src = fullBase64;
        nameEl.innerText = file.name.slice(0, 20);
        preview.style.display = 'flex';
        sfx.playClick();
    };
    reader.readAsDataURL(file);
}

function clearAttachment() {
    appState.attachedImage = null;
    document.getElementById('attachment-preview').style.display = 'none';
    document.getElementById('file-input').value = '';
}

function openLightbox(url) {
    const modal = document.getElementById('lightbox-modal');
    const img = document.getElementById('lightbox-img');
    const dl = document.getElementById('lightbox-download');
    img.src = url;
    dl.href = url;
    modal.style.display = 'flex';
    sfx.playClick();
}

function closeLightbox() {
    document.getElementById('lightbox-modal').style.display = 'none';
}

// ----------------- Markdown Formatter Utility -----------------

function formatMarkdown(text) {
    if (!text) return '';

    // Extract code blocks first to protect them from inline formatting
    const codeBlocks = [];
    let processed = text.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
        const langLabel = lang || 'code';
        const codeId = 'code_' + Math.random().toString(36).substr(2, 9);
        const placeholder = `__CODE_BLOCK_${codeBlocks.length}__`;
        codeBlocks.push(`
            <div class="code-block">
                <div class="code-header">
                    <span>${langLabel}</span>
                    <button class="code-copy-btn" onclick="copyCodeSnippet('${codeId}')">
                        ${ICONS.copy} نسخ الكود
                    </button>
                </div>
                <pre><code id="${codeId}">${escapeHtml(code.trim())}</code></pre>
            </div>
        `);
        return placeholder;
    });

    // Escape basic HTML outside code blocks
    processed = escapeHtml(processed);

    // Headers
    processed = processed.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    processed = processed.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    processed = processed.replace(/^# (.+)$/gm, '<h1>$1</h1>');

    // Bold & Italic
    processed = processed.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    processed = processed.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Inline code
    processed = processed.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Process lists and paragraphs line by line
    const lines = processed.split('\n');
    const result = [];
    let inUl = false;
    let inOl = false;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();

        const ulMatch = trimmed.match(/^[-*•]\s+(.+)$/);
        const olMatch = trimmed.match(/^(\d+)[.)]\s+(.+)$/);

        if (ulMatch) {
            if (inOl) { result.push('</ol>'); inOl = false; }
            if (!inUl) { result.push('<ul>'); inUl = true; }
            result.push(`<li>${ulMatch[1]}</li>`);
        } else if (olMatch) {
            if (inUl) { result.push('</ul>'); inUl = false; }
            if (!inOl) { result.push('<ol>'); inOl = true; }
            result.push(`<li>${olMatch[2]}</li>`);
        } else {
            if (inUl) { result.push('</ul>'); inUl = false; }
            if (inOl) { result.push('</ol>'); inOl = false; }

            if (trimmed.length > 0) {
                if (trimmed.startsWith('<h') || trimmed.startsWith('__CODE_BLOCK_')) {
                    result.push(trimmed);
                } else {
                    result.push(`<p>${trimmed}</p>`);
                }
            }
        }
    }

    if (inUl) result.push('</ul>');
    if (inOl) result.push('</ol>');

    let finalHtml = result.join('');

    // Restore code blocks
    for (let i = 0; i < codeBlocks.length; i++) {
        finalHtml = finalHtml.replace(`__CODE_BLOCK_${i}__`, codeBlocks[i]);
    }

    return finalHtml;
}

function escapeHtml(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function copyText(msgId) {
    const chat = getCurrentChat();
    if (!chat) return;
    const msg = chat.messages.find(m => m.id === msgId);
    if (msg) {
        navigator.clipboard.writeText(msg.text);
        sfx.playClick();
    }
}

function copyCodeSnippet(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        navigator.clipboard.writeText(el.innerText);
        sfx.playClick();
    }
}

// ----------------- Mobile & Settings Modal Navigation -----------------

function isMobile() {
    return window.innerWidth <= 900;
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (isMobile()) {
        const isOpen = sidebar.classList.contains('open');
        if (isOpen) {
            sidebar.classList.remove('open');
            overlay.classList.remove('open');
        } else {
            sidebar.classList.add('open');
            overlay.classList.add('open');
        }
    } else {
        const isCollapsed = sidebar.classList.toggle('collapsed');
        localStorage.setItem('movita_ai_sidebar_collapsed', isCollapsed);
    }
    sfx.playClick();
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (isMobile()) {
        sidebar.classList.remove('open');
        overlay.classList.remove('open');
    } else {
        sidebar.classList.add('collapsed');
        localStorage.setItem('movita_ai_sidebar_collapsed', 'true');
    }
    sfx.playClick();
}

function openSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (isMobile()) {
        sidebar.classList.add('open');
        overlay.classList.add('open');
    } else {
        sidebar.classList.remove('collapsed');
        localStorage.setItem('movita_ai_sidebar_collapsed', 'false');
    }
    sfx.playClick();
}

function initSidebarState() {
    const sidebar = document.getElementById('sidebar');
    if (!isMobile()) {
        const saved = localStorage.getItem('movita_ai_sidebar_collapsed');
        if (saved === 'true') {
            sidebar.classList.add('collapsed');
        }
    }
}

function openSettings() {
    document.getElementById('settings-modal').style.display = 'flex';
    document.getElementById('setting-persona').value = appState.persona;
    document.getElementById('setting-tts').checked = appState.ttsEnabled;
    document.getElementById('setting-sounds').checked = appState.soundEnabled;
    sfx.playClick();
}

function closeSettings() {
    document.getElementById('settings-modal').style.display = 'none';
}

function saveSettings() {
    appState.persona = document.getElementById('setting-persona').value;
    appState.ttsEnabled = document.getElementById('setting-tts').checked;
    appState.soundEnabled = document.getElementById('setting-sounds').checked;

    localStorage.setItem(SETTINGS_KEY, JSON.stringify({
        persona: appState.persona,
        ttsEnabled: appState.ttsEnabled,
        soundEnabled: appState.soundEnabled
    }));

    closeSettings();
    sfx.playClick();
}

function initCard3DHover() {
    if (window.innerWidth <= 900 || /Android|iPhone|Mobile/i.test(navigator.userAgent)) return;
    document.querySelectorAll('.prompt-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -8;
            const rotateY = ((x - centerX) / centerX) * 8;
            card.style.transform = `perspective(800px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateY(-6px) scale3d(1.03, 1.03, 1.03)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg) translateY(0) scale3d(1, 1, 1)';
        });
    });
}

function initHero3DParallax() {
    if (window.innerWidth <= 900 || /Android|iPhone|Mobile/i.test(navigator.userAgent)) return;
    const avatarBox = document.getElementById('hero-avatar-box');
    const welcomeScreen = document.getElementById('welcome-screen');
    if (!avatarBox || !welcomeScreen) return;

    welcomeScreen.addEventListener('mousemove', (e) => {
        const rect = avatarBox.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const dx = e.clientX - centerX;
        const dy = e.clientY - centerY;
        const rotateY = (dx / 22).toFixed(2);
        const rotateX = (-dy / 22).toFixed(2);
        avatarBox.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.05)`;
    });

    welcomeScreen.addEventListener('mouseleave', () => {
        avatarBox.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg) scale(1)';
    });
}

function initMagneticElements() {
    if (window.innerWidth <= 900 || /Android|iPhone|Mobile/i.test(navigator.userAgent)) return;
    const elements = document.querySelectorAll('.send-btn, .new-chat-btn, .action-circle-btn, .icon-btn');
    elements.forEach(el => {
        el.addEventListener('mousemove', (e) => {
            const rect = el.getBoundingClientRect();
            const x = e.clientX - (rect.left + rect.width / 2);
            const y = e.clientY - (rect.top + rect.height / 2);
            el.style.transform = `translate(${x * 0.28}px, ${y * 0.28}px) scale(1.08)`;
        });
        el.addEventListener('mouseleave', () => {
            el.style.transform = '';
        });
    });
}

// ----------------- Event Listeners Initialization -----------------

document.addEventListener('DOMContentLoaded', () => {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    initAmbientCanvas();
    initSidebarState();
    initCard3DHover();
    initHero3DParallax();
    initMagneticElements();
    loadSessions();

    // New Chat Button
    document.getElementById('new-chat-btn').onclick = createNewChat;

    // Search History
    document.getElementById('search-chats').oninput = renderSidebar;

    // Clear All Chats
    document.getElementById('clear-all-chats-btn').onclick = clearAllChats;

    // Sidebar Toggles (Desktop & Mobile)
    document.getElementById('mobile-menu-btn').onclick = toggleSidebar;
    document.getElementById('close-sidebar-btn').onclick = closeSidebar;
    document.getElementById('sidebar-overlay').onclick = closeSidebar;

    // Send Button & Enter Key
    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) {
        sendBtn.onclick = handleSendMessage;
        sendBtn.addEventListener('click', handleSendMessage);
    }
    const inputArea = document.getElementById('user-input');
    if (inputArea) {
        inputArea.addEventListener('keydown', (e) => {
            if ((e.key === 'Enter' || e.keyCode === 13) && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });
    }

    // Auto-grow textarea
    inputArea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 160) + 'px';
    });

    // Quick Prompt Cards click handler
    document.querySelectorAll('.prompt-card').forEach(card => {
        card.onclick = () => {
            const prompt = card.getAttribute('data-prompt');
            inputArea.value = prompt;
            handleSendMessage();
        };
    });

    // File Upload
    const fileInput = document.getElementById('file-input');
    document.getElementById('upload-btn').onclick = () => fileInput.click();
    fileInput.onchange = handleFileUpload;
    document.getElementById('remove-attachment-btn').onclick = clearAttachment;

    // Magic Image Generator Shortcut button
    document.getElementById('magic-image-btn').onclick = () => {
        inputArea.value = '/image ';
        inputArea.focus();
        sfx.playClick();
    };

    // Voice Recording Buttons
    document.getElementById('mic-btn').onclick = startRecording;
    document.getElementById('rec-finish-btn').onclick = () => stopRecording(true);
    document.getElementById('rec-cancel-btn').onclick = () => stopRecording(false);

    // Lightbox Modal
    document.getElementById('lightbox-close-btn').onclick = closeLightbox;
    document.getElementById('lightbox-backdrop').onclick = closeLightbox;

    // Settings Modal
    document.getElementById('settings-btn').onclick = openSettings;
    document.getElementById('settings-close-btn').onclick = closeSettings;
    document.getElementById('settings-backdrop').onclick = closeSettings;
    document.getElementById('save-settings-btn').onclick = saveSettings;

    // Sound Toggle in Header
    const soundToggle = document.getElementById('sound-toggle-btn');
    soundToggle.onclick = () => {
        appState.soundEnabled = !appState.soundEnabled;
        soundToggle.innerHTML = appState.soundEnabled ? ICONS.volumeHigh : ICONS.volumeMute;
        sfx.playClick();
    };
});
