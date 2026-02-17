/**
 * LOKAAH - Enhanced Single Tutor Frontend
 * Invisible multi-agent handoff with premium UX
 * Version: 2.0 - Production Ready
 */

document.addEventListener('DOMContentLoaded', () => {
    initChat();
    initSidebar();
});

const API_BASE = (() => {
    const host = window.location.hostname;
    const protocol = window.location.protocol;
    if (protocol === 'file:' || host === 'localhost' || host === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    return '';
})();

const SESSION_KEY = 'lokaah_chat_session';

// Single unified tutor persona (hides multi-agent system)
const TUTOR_PERSONA = {
    name: 'LOKAAH',
    avatar: '🎓',
    greeting: 'Hey! I\'m your AI tutor. Ready to make learning fun?'
};

// Internal agent tracking (invisible to user)
const AGENT_META = {
    veda: { label: 'Teaching', color: 'blue', status: 'Learning mode active' },
    oracle: { label: 'Practice', color: 'purple', status: 'Practice mode active' },
    spark: { label: 'Challenge', color: 'orange', status: 'Challenge mode active' },
    pulse: { label: 'Wellbeing', color: 'green', status: 'Wellbeing mode active' },
    atlas: { label: 'Planning', color: 'teal', status: 'Planning mode active' }
};

function initChat() {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');
    const messagesContainer = document.getElementById('messages');
    const statusText = document.getElementById('status-text');

    if (!form || !input || !messagesContainer) {
        console.error('Chat elements not found');
        return;
    }

    const state = {
        sessionId: getOrCreateSession(),
        activeAgent: 'veda',
        messageHistory: []
    };

    // Welcome message
    addMessage({
        role: 'bot',
        text: TUTOR_PERSONA.greeting,
        agentName: 'veda'
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = input.value.trim();
        if (!message) return;

        // Add user message
        addMessage({ role: 'user', text: message });
        input.value = '';
        input.disabled = true;

        // Show typing indicator
        const typingEl = addTypingIndicator();
        setTransientStatus('Thinking...');

        try {
            await handleStreamingChat(message, state, null, typingEl);
        } catch (error) {
            console.error('Chat error:', error);
            removeTypingIndicator(typingEl);
            await fallbackFetch(message, state, null, typingEl);
        } finally {
            input.disabled = false;
            input.focus();
        }
    });

    function setTransientStatus(text) {
        if (statusText) {
            statusText.textContent = text;
            setTimeout(() => {
                const agentStatus = AGENT_META[state.activeAgent]?.status || 'Ready';
                statusText.textContent = agentStatus;
            }, 2000);
        }
    }

    async function handleStreamingChat(message, state, forceAgent, typingEl) {
        const response = await fetch(`${API_BASE}/api/v1/chat/stream`, {
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
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let currentEvent = null;
        let fullText = '';
        let botMessageEl = null;
        let botTextEl = null;
        let metaReceived = false;

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('event:')) {
                    currentEvent = line.substring(6).trim();
                } else if (line.startsWith('data:')) {
                    const dataStr = line.substring(5).trim();
                    if (!dataStr) continue;

                    let data;
                    try {
                        data = JSON.parse(dataStr);
                    } catch {
                        continue;
                    }

                    if (currentEvent === 'meta') {
                        metaReceived = true;
                        removeTypingIndicator(typingEl);
                        state.activeAgent = data.agent_name || 'veda';

                        // Create message element (without showing agent name)
                        const msgObj = addMessage({
                            role: 'bot',
                            text: '',
                            agentName: state.activeAgent
                        });
                        botMessageEl = msgObj.messageEl;
                        botTextEl = msgObj.textEl;

                        if (botTextEl) {
                            botTextEl.classList.add('streaming');
                        }

                        setTransientStatus(AGENT_META[state.activeAgent]?.status || 'Responding...');
                    } else if (currentEvent === 'token' && botTextEl) {
                        fullText += data.text;
                        botTextEl.innerHTML = formatMessage(fullText);
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    } else if (currentEvent === 'done') {
                        if (botTextEl) {
                            botTextEl.classList.remove('streaming');
                            // Render LaTeX math
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
                        }
                        setTransientStatus('Ready');
                    } else if (currentEvent === 'error') {
                        removeTypingIndicator(typingEl);
                        addMessage({
                            role: 'bot',
                            text: data.text || "Hmm, something went wrong. Could you try again?",
                            agentName: state.activeAgent
                        });
                    }
                    currentEvent = null;
                }
            }
        }

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
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        removeTypingIndicator(typingEl);
        state.activeAgent = data.agent_name || 'veda';

        addMessage({
            role: 'bot',
            text: data.response,
            agentName: state.activeAgent
        });
    }

    function addMessage({ role, text, agentName }) {
        const messageDiv = document.createElement('div');

        if (role === 'user') {
            messageDiv.className = 'chat-message user';
            messageDiv.innerHTML = `
                <div class="message-avatar user-avatar">Y</div>
                <div class="message-content">
                    <div class="message-text">${formatMessage(text)}</div>
                </div>
            `;
        } else {
            // Bot message - UNIFIED tutor (no agent name shown)
            const safeAgent = agentName || 'veda';
            const agentColor = AGENT_META[safeAgent]?.color || 'blue';

            messageDiv.className = `chat-message bot agent-${agentColor}`;
            messageDiv.innerHTML = `
                <div class="message-avatar bot-avatar">${TUTOR_PERSONA.avatar}</div>
                <div class="message-content">
                    <div class="message-text"></div>
                </div>
            `;
        }

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        const textEl = messageDiv.querySelector('.message-text');
        if (role === 'bot' && textEl) {
            textEl.innerHTML = formatMessage(text);
        }

        return {
            messageEl: messageDiv,
            textEl: textEl
        };
    }

    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar bot-avatar">${TUTOR_PERSONA.avatar}</div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return typingDiv;
    }

    function removeTypingIndicator(el) {
        if (el && el.parentNode) {
            el.parentNode.removeChild(el);
        }
    }
}

function formatMessage(text) {
    if (!text) return '';

    // Enhanced formatting
    let formatted = escapeHtml(text);

    // Preserve LaTeX
    formatted = formatted
        .replace(/\\\(/g, '\\(')
        .replace(/\\\)/g, '\\)')
        .replace(/\\\[/g, '\\[')
        .replace(/\\\]/g, '\\]');

    // Convert markdown-style formatting
    formatted = formatted
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`(.+?)`/g, '<code>$1</code>');

    // Convert newlines to breaks
    formatted = formatted.replace(/\n/g, '<br>');

    // Checkmarks and emojis
    formatted = formatted
        .replace(/✅/g, '<span class="check-mark">✅</span>')
        .replace(/❌/g, '<span class="cross-mark">❌</span>');

    return formatted;
}

function escapeHtml(unsafe) {
    const div = document.createElement('div');
    div.textContent = unsafe;
    return div.innerHTML;
}

function getOrCreateSession() {
    let sessionId = localStorage.getItem(SESSION_KEY);
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem(SESSION_KEY, sessionId);
    }
    return sessionId;
}

function initSidebar() {
    // Sidebar toggle logic
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }
}
