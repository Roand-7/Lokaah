/**
 * LOKAAH - Single Chat Frontend
 * One chat contact with invisible multi-agent handoff.
 * Uses SSE streaming for fluid, token-by-token responses.
 */

document.addEventListener('DOMContentLoaded', () => {
    initChat();
    initSidebar();
});

const API_BASE = (() => {
    const host = window.location.hostname;
    const protocol = window.location.protocol;
    if (protocol === 'file:' || host === 'localhost' || host === '127.0.0.1') {
        return 'http://localhost:8001';  // Updated from 8000 to 8001
    }
    return '';
})();

const SESSION_KEY = 'lokaah_chat_session';

const AGENT_META = {
    veda: {
        label: 'VEDA',
        emoji: 'V',
        color: 'blue',
        status: 'Teaching mode active'
    },
    oracle: {
        label: 'ORACLE',
        emoji: 'O',
        color: 'purple',
        status: 'Practice mode active'
    },
    spark: {
        label: 'SPARK',
        emoji: 'S',
        color: 'orange',
        status: 'Challenge mode active'
    },
    pulse: {
        label: 'PULSE',
        emoji: 'P',
        color: 'green',
        status: 'Wellbeing mode active'
    },
    atlas: {
        label: 'ATLAS',
        emoji: 'A',
        color: 'teal',
        status: 'Planning mode active'
    }
};

function initChat() {
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const messagesContainer = document.getElementById('messagesContainer');
    const welcomeScreen = document.getElementById('welcomeScreen');

    if (!messageInput || !sendBtn || !messagesContainer) return;

    const state = {
        sessionId: localStorage.getItem(SESSION_KEY) || null,
        activeAgent: 'veda',
        isStreaming: false
    };

    applyAgentTheme('veda');

    messageInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 150) + 'px';
        sendBtn.disabled = !this.value.trim() || state.isStreaming;
    });

    messageInput.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            if (this.value.trim() && !state.isStreaming) {
                sendMessage(this.value.trim());
            }
        }
    });

    sendBtn.addEventListener('click', () => {
        if (messageInput.value.trim() && !state.isStreaming) {
            sendMessage(messageInput.value.trim());
        }
    });

    document.querySelectorAll('.quick-action, .command-chip').forEach(btn => {
        btn.addEventListener('click', () => {
            const text = btn.dataset.message;
            if (text && !state.isStreaming) sendMessage(text);
        });
    });

    async function sendMessage(rawText) {
        if (welcomeScreen) welcomeScreen.style.display = 'none';

        addMessage({ role: 'user', text: rawText });

        messageInput.value = '';
        messageInput.style.height = 'auto';
        sendBtn.disabled = true;
        state.isStreaming = true;

        const { forceAgent, cleanText } = parseForceAgent(rawText);
        const outboundMessage = cleanText || rawText;

        setTransientStatus('Lokaah is thinking...');
        const typingEl = showTypingIndicator(state.activeAgent);

        try {
            // Try SSE streaming first, fall back to regular fetch
            await streamFromAPI(outboundMessage, state, forceAgent, typingEl);
        } catch (error) {
            removeTypingIndicator(typingEl);

            const fallback = getFallbackResponse(rawText, forceAgent);
            state.activeAgent = fallback.agentName;
            applyAgentTheme(fallback.agentName);

            addMessage({
                role: 'bot',
                text: fallback.text,
                agentName: fallback.agentName,
                agentLabel: AGENT_META[fallback.agentName].label,
                agentEmoji: AGENT_META[fallback.agentName].emoji
            });
        }

        state.isStreaming = false;
        sendBtn.disabled = !messageInput.value.trim();
    }

    async function streamFromAPI(message, state, forceAgent, typingEl) {
        const body = JSON.stringify({
            message,
            session_id: state.sessionId,
            user_profile: { channel: 'web_lokaah' },
            force_agent: forceAgent || null
        });

        const response = await fetch(`${API_BASE}/api/v1/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body
        });

        if (!response.ok) {
            // Fall back to non-streaming endpoint
            return await fallbackFetch(message, state, forceAgent, typingEl);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let botMessageEl = null;
        let botTextEl = null;
        let fullText = '';
        let metaReceived = false;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('event: ')) {
                    var currentEvent = line.slice(7).trim();
                } else if (line.startsWith('data: ') && currentEvent) {
                    const data = JSON.parse(line.slice(6));

                    if (currentEvent === 'meta') {
                        // Agent info arrived - update theme and create message bubble
                        if (data.session_id) {
                            state.sessionId = data.session_id;
                            localStorage.setItem(SESSION_KEY, data.session_id);
                        }
                        state.activeAgent = data.agent_name || 'veda';
                        applyAgentTheme(state.activeAgent);
                        removeTypingIndicator(typingEl);

                        const result = createBotMessageElement(
                            data.agent_name,
                            data.agent_label,
                            data.agent_emoji
                        );
                        botMessageEl = result.messageDiv;
                        botTextEl = result.textEl;
                        messagesContainer.appendChild(botMessageEl);
                        metaReceived = true;
                    } else if (currentEvent === 'token' && metaReceived) {
                        fullText += data.text;
                        botTextEl.innerHTML = formatMessage(fullText);
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    } else if (currentEvent === 'done') {
                        // Remove streaming cursor
                        if (botTextEl) botTextEl.classList.remove('streaming');
                        // Render math if KaTeX available
                        if (botMessageEl && typeof renderMathInElement !== 'undefined') {
                            renderMathInElement(botMessageEl, {
                                delimiters: [
                                    { left: '$$', right: '$$', display: true },
                                    { left: '$', right: '$', display: false },
                                    { left: '\\(', right: '\\)', display: false },
                                    { left: '\\[', right: '\\]', display: true }
                                ],
                                throwOnError: false
                            });
                        }
                        setTransientStatus(AGENT_META[state.activeAgent]?.status || 'Ready');
                    } else if (currentEvent === 'error') {
                        removeTypingIndicator(typingEl);
                        addMessage({
                            role: 'bot',
                            text: data.text || "Hmm, something went wrong. Could you try again?",
                            agentName: state.activeAgent,
                            agentLabel: AGENT_META[state.activeAgent]?.label || 'VEDA',
                            agentEmoji: AGENT_META[state.activeAgent]?.emoji || 'V'
                        });
                    }
                    currentEvent = null;
                }
            }
        }

        // If stream ended but no meta event received, it's an error
        if (!metaReceived) {
            throw new Error('Stream ended without meta event');
        }
    }

    async function fallbackFetch(message, state, forceAgent, typingEl) {
        const response = await fetch(`${API_BASE}/api/v1/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message,
                session_id: state.sessionId,
                user_profile: { channel: 'web_lokaah' },
                force_agent: forceAgent || null
            })
        });

        if (!response.ok) {
            throw new Error(`API error ${response.status}`);
        }

        const data = await response.json();

        if (data.session_id) {
            state.sessionId = data.session_id;
            localStorage.setItem(SESSION_KEY, data.session_id);
        }

        state.activeAgent = data.agent_name || 'veda';
        removeTypingIndicator(typingEl);
        applyAgentTheme(state.activeAgent);

        addMessage({
            role: 'bot',
            text: data.response || 'I can help. Tell me what you want to focus on.',
            agentName: data.agent_name,
            agentLabel: data.agent_label,
            agentEmoji: data.agent_emoji
        });
    }

    function createBotMessageElement(agentName, agentLabel, agentEmoji) {
        const safeAgent = agentName || 'veda';
        const meta = AGENT_META[safeAgent] || AGENT_META.veda;
        const author = agentLabel || meta.label;
        const avatar = agentEmoji || meta.emoji;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message bot agent-${safeAgent}`;

        const textEl = document.createElement('div');
        textEl.className = 'message-text streaming';

        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-author">${escapeHtml(author)}</div>
            </div>
        `;
        messageDiv.querySelector('.message-content').appendChild(textEl);

        return { messageDiv, textEl };
    }

    function addMessage({ role, text, agentName, agentLabel, agentEmoji }) {
        const messageDiv = document.createElement('div');

        if (role === 'user') {
            messageDiv.className = 'chat-message user';
            messageDiv.innerHTML = `
                <div class="message-avatar">Y</div>
                <div class="message-content">
                    <div class="message-author">You</div>
                    <div class="message-text">${formatMessage(text)}</div>
                </div>
            `;
        } else {
            const safeAgent = agentName || 'veda';
            const meta = AGENT_META[safeAgent] || AGENT_META.veda;
            const author = agentLabel || meta.label;
            const avatar = agentEmoji || meta.emoji;

            messageDiv.className = `chat-message bot agent-${safeAgent}`;
            messageDiv.innerHTML = `
                <div class="message-avatar">${avatar}</div>
                <div class="message-content">
                    <div class="message-author">${escapeHtml(author)}</div>
                    <div class="message-text">${formatMessage(text)}</div>
                </div>
            `;
        }

        messagesContainer.appendChild(messageDiv);

        if (typeof renderMathInElement !== 'undefined') {
            renderMathInElement(messageDiv, {
                delimiters: [
                    { left: '$$', right: '$$', display: true },
                    { left: '$', right: '$', display: false },
                    { left: '\\(', right: '\\)', display: false },
                    { left: '\\[', right: '\\]', display: true }
                ],
                throwOnError: false
            });
        }

        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

function parseForceAgent(text) {
    const message = (text || '').trim();
    if (!message.startsWith('/')) {
        return { forceAgent: null, cleanText: message };
    }

    const parts = message.split(' ');
    const command = parts[0].toLowerCase();
    const cleanText = parts.slice(1).join(' ').trim();

    const map = {
        '/test': 'oracle',
        '/spark': 'spark',
        '/chill': 'pulse',
        '/plan': 'atlas',
        '/veda': 'veda',
        '/oracle': 'oracle',
        '/pulse': 'pulse',
        '/atlas': 'atlas'
    };

    return {
        forceAgent: map[command] || null,
        cleanText
    };
}

function applyAgentTheme(agentName) {
    const meta = AGENT_META[agentName] || AGENT_META.veda;

    const chatMain = document.getElementById('chatMain');
    const badge = document.getElementById('agentBadge');
    const status = document.getElementById('agentStatus');

    if (chatMain) {
        chatMain.classList.remove('agent-veda', 'agent-oracle', 'agent-spark', 'agent-pulse', 'agent-atlas');
        chatMain.classList.add(`agent-${agentName}`);
    }

    if (badge) {
        badge.textContent = `LOKAAH AI`;
    }

    if (status) {
        status.textContent = meta.status;
    }
}

function showTypingIndicator(agentName) {
    const messagesContainer = document.getElementById('messagesContainer');
    if (!messagesContainer) return null;

    const meta = AGENT_META[agentName] || AGENT_META.veda;

    const typingDiv = document.createElement('div');
    typingDiv.className = `typing-bubble agent-${agentName}`;
    typingDiv.innerHTML = `
        <div class="message-avatar">${meta.emoji}</div>
        <div class="typing-content">
            <div class="typing-label">${meta.label} is thinking...</div>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return typingDiv;
}

function removeTypingIndicator(element) {
    if (element && element.parentNode) {
        element.parentNode.removeChild(element);
    }
}

function setTransientStatus(text) {
    const status = document.getElementById('agentStatus');
    if (status) {
        status.textContent = text;
    }
}

function formatMessage(rawText) {
    const safe = escapeHtml(rawText || '');

    return safe
        .replace(/```([\s\S]*?)```/g, '<pre>$1</pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function getFallbackResponse(message, forceAgent) {
    const msg = (message || '').toLowerCase();

    if (forceAgent === 'pulse' || msg.includes('anxious') || msg.includes('panic') || msg.includes('stupid')) {
        return {
            agentName: 'pulse',
            text: 'You are not behind forever. Take one deep breath with me, then we solve one small step and build momentum.'
        };
    }

    if (forceAgent === 'atlas' || msg.includes('plan') || msg.includes('schedule') || msg.includes('exam date')) {
        return {
            agentName: 'atlas',
            text: 'Plan mode: Monday trigonometry, Wednesday quadratics, Friday probability drill, Sunday full revision. Want a daily checklist?'
        };
    }

    if (forceAgent === 'spark' || msg.includes('challenge') || msg.includes('hard')) {
        return {
            agentName: 'spark',
            text: 'Challenge mode: A tower is observed at 30 deg and 60 deg from two points 20 m apart. Find the height.'
        };
    }

    if (forceAgent === 'oracle' || msg.includes('question') || msg.includes('practice') || msg.includes('test')) {
        return {
            agentName: 'oracle',
            text: 'Practice mode: Solve x^2 - 7x + 12 = 0 and verify by substitution.'
        };
    }

    return {
        agentName: 'veda',
        text: 'Let us learn step by step. Tell me the exact concept where you feel stuck and I will break it down clearly.'
    };
}

function initSidebar() {
    const menuBtn = document.getElementById('menuBtn');
    const sidebar = document.getElementById('sidebar');
    const sidebarClose = document.getElementById('sidebarClose');
    const newChatBtn = document.getElementById('newChatBtn');

    if (!menuBtn || !sidebar) return;

    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);

    menuBtn.addEventListener('click', () => {
        sidebar.classList.add('open');
        overlay.classList.add('active');
    });

    function closeSidebar() {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
    }

    if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
    overlay.addEventListener('click', closeSidebar);

    if (newChatBtn) {
        newChatBtn.addEventListener('click', () => {
            const messagesContainer = document.getElementById('messagesContainer');
            const welcomeScreen = document.getElementById('welcomeScreen');

            localStorage.removeItem(SESSION_KEY);

            if (messagesContainer) {
                const messages = messagesContainer.querySelectorAll('.chat-message, .typing-bubble');
                messages.forEach(msg => msg.remove());
            }

            if (welcomeScreen) {
                welcomeScreen.style.display = 'flex';
            }

            applyAgentTheme('veda');
            closeSidebar();
        });
    }
}
