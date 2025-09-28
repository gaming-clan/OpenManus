// OpenManus Frontend Application
class OpenManusApp {
    constructor() {
        this.currentMode = 'agent';
        this.chatHistory = [];
        this.agentLogs = '';
        this.isLoading = false;
        this.autoRefreshInterval = null;
        this.autoRefreshEnabled = true;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadAgentLogs();
        this.showMode('agent');
        this.startAutoRefresh();
    }

    bindEvents() {
        // Navigation events
        document.getElementById('agent-mode-btn').addEventListener('click', () => {
            this.showMode('agent');
        });

        document.getElementById('chat-mode-btn').addEventListener('click', () => {
            this.showMode('chat');
        });

        // Agent mode events
        document.getElementById('refresh-logs-btn').addEventListener('click', () => {
            this.loadAgentLogs();
        });

        document.getElementById('start-agent-btn').addEventListener('click', () => {
            this.startAgent();
        });

        document.getElementById('stop-agent-btn').addEventListener('click', () => {
            this.stopAgent();
        });

        // Chat mode events
        document.getElementById('send-button').addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('clear-chat-btn').addEventListener('click', () => {
            this.clearChat();
        });

        // Chat textarea events
        const textarea = document.getElementById('chat-textarea');
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        textarea.addEventListener('input', () => {
            this.autoResizeTextarea(textarea);
        });

        // Window visibility change event for auto-refresh
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAutoRefresh();
            } else {
                this.resumeAutoRefresh();
            }
        });
    }

    showMode(mode) {
        // Update navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(`${mode}-mode-btn`).classList.add('active');

        // Update mode sections
        document.querySelectorAll('.mode-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${mode}-mode`).classList.add('active');

        this.currentMode = mode;

        // Load data for the current mode
        if (mode === 'agent') {
            this.loadAgentLogs();
            this.resumeAutoRefresh();
        } else {
            this.pauseAutoRefresh();
        }
    }

    // Agent Mode Functions
    async loadAgentLogs() {
        const logsElement = document.getElementById('agent-logs');
        const refreshBtn = document.getElementById('refresh-logs-btn');
        
        try {
            refreshBtn.disabled = true;
            refreshBtn.textContent = 'Loading...';

            const response = await this.fetchWithTimeout('/api/agent/logs', {}, 10000);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.agentLogs = data.logs ? data.logs.join('\n') : 'No logs available';
            logsElement.textContent = this.agentLogs;
            
            // Auto-scroll to bottom
            logsElement.scrollTop = logsElement.scrollHeight;
            
            // Update last refresh time
            this.updateLastRefreshTime();
            
        } catch (error) {
            console.error('Error loading agent logs:', error);
            const errorMessage = this.getErrorMessage(error);
            logsElement.textContent = `Error loading logs: ${errorMessage}\n\nPlease check if the backend server is running and the API endpoint is available.`;
        } finally {
            refreshBtn.disabled = false;
            refreshBtn.textContent = 'Refresh Logs';
        }
    }

    async startAgent() {
        const startBtn = document.getElementById('start-agent-btn');
        const agentSelect = document.getElementById('agent-select');
        
        try {
            startBtn.disabled = true;
            startBtn.textContent = 'Starting...';

            const response = await this.fetchWithTimeout('/api/agent/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    agent_type: agentSelect.value
                })
            }, 15000);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification('Agent started successfully', 'success');
            } else {
                throw new Error(data.message || 'Unknown error starting agent');
            }
            
            // Refresh logs after starting
            setTimeout(() => this.loadAgentLogs(), 1000);
            
        } catch (error) {
            console.error('Error starting agent:', error);
            const errorMessage = this.getErrorMessage(error);
            this.showNotification(`Error starting agent: ${errorMessage}`, 'error');
        } finally {
            startBtn.disabled = false;
            startBtn.textContent = 'Start Agent';
        }
    }

    async stopAgent() {
        const stopBtn = document.getElementById('stop-agent-btn');
        
        try {
            stopBtn.disabled = true;
            stopBtn.textContent = 'Stopping...';

            const response = await this.fetchWithTimeout('/api/agent/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            }, 15000);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification('Agent stopped successfully', 'success');
            } else {
                throw new Error(data.message || 'Unknown error stopping agent');
            }
            
            // Refresh logs after stopping
            setTimeout(() => this.loadAgentLogs(), 1000);
            
        } catch (error) {
            console.error('Error stopping agent:', error);
            const errorMessage = this.getErrorMessage(error);
            this.showNotification(`Error stopping agent: ${errorMessage}`, 'error');
        } finally {
            stopBtn.disabled = false;
            stopBtn.textContent = 'Stop Agent';
        }
    }

    // Chat Mode Functions
    async sendMessage() {
        const textarea = document.getElementById('chat-textarea');
        const sendBtn = document.getElementById('send-button');
        const message = textarea.value.trim();

        if (!message || this.isLoading) {
            return;
        }

        try {
            this.isLoading = true;
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';

            // Add user message to history
            this.addMessageToHistory('user', message);
            textarea.value = '';
            this.autoResizeTextarea(textarea);

            // Add loading message for agent
            const loadingId = this.addMessageToHistory('agent', 'Thinking...');

            const response = await this.fetchWithTimeout('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: message })
            }, 30000);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Update the loading message with the actual response
            const agentResponse = data.output || 'No response received';
            this.updateMessageInHistory(loadingId, agentResponse);

            // Show error notification if there was an error in the response
            if (data.error) {
                this.showNotification('Agent responded with an error', 'warning');
            }

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = this.getErrorMessage(error);
            this.updateMessageInHistory(loadingId, `Error: ${errorMessage}`);
            this.showNotification(`Error sending message: ${errorMessage}`, 'error');
        } finally {
            this.isLoading = false;
            sendBtn.disabled = false;
            sendBtn.textContent = 'Send';
            textarea.focus();
        }
    }

    addMessageToHistory(sender, message) {
        const historyElement = document.getElementById('chat-history');
        const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-entry';
        messageElement.innerHTML = `
            <div class="${sender}" id="${messageId}">${this.escapeHtml(message)}</div>
        `;
        
        historyElement.appendChild(messageElement);
        
        // Auto-scroll to bottom
        historyElement.scrollTop = historyElement.scrollHeight;
        
        // Store in chat history
        this.chatHistory.push({ sender, message, id: messageId });
        
        return messageId;
    }

    updateMessageInHistory(messageId, newMessage) {
        const messageElement = document.getElementById(messageId);
        if (messageElement) {
            messageElement.textContent = newMessage;
        }
        
        // Update in chat history array
        const historyItem = this.chatHistory.find(item => item.id === messageId);
        if (historyItem) {
            historyItem.message = newMessage;
        }
    }

    clearChat() {
        const historyElement = document.getElementById('chat-history');
        historyElement.innerHTML = '';
        this.chatHistory = [];
        this.showNotification('Chat cleared', 'success');
    }

    // Auto-refresh functionality
    startAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        
        this.autoRefreshInterval = setInterval(() => {
            if (this.currentMode === 'agent' && this.autoRefreshEnabled && !this.isLoading && !document.hidden) {
                this.loadAgentLogs();
            }
        }, 30000); // Refresh every 30 seconds
    }

    pauseAutoRefresh() {
        this.autoRefreshEnabled = false;
    }

    resumeAutoRefresh() {
        this.autoRefreshEnabled = true;
        if (this.currentMode === 'agent') {
            this.loadAgentLogs();
        }
    }

    // Utility Functions
    async fetchWithTimeout(url, options = {}, timeout = 10000) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timed out');
            }
            throw error;
        }
    }

    getErrorMessage(error) {
        if (error.message.includes('Failed to fetch')) {
            return 'Unable to connect to server. Please check if the backend is running.';
        } else if (error.message.includes('timed out')) {
            return 'Request timed out. The server may be overloaded.';
        } else {
            return error.message;
        }
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    updateLastRefreshTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        
        // Add a small indicator showing last refresh time
        const refreshBtn = document.getElementById('refresh-logs-btn');
        const originalText = refreshBtn.textContent;
        refreshBtn.title = `Last refreshed: ${timeString}`;
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => {
            notification.remove();
        });

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add styles
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '600',
            zIndex: '1000',
            opacity: '0',
            transform: 'translateY(-20px)',
            transition: 'all 0.3s ease',
            maxWidth: '300px',
            wordWrap: 'break-word',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
        });

        // Set background color based on type
        const colors = {
            success: '#48bb78',
            error: '#f56565',
            info: '#667eea',
            warning: '#ed8936'
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        // Add to DOM
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 10);

        // Remove after 4 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new OpenManusApp();
    
    // Make app globally available for debugging
    window.openManusApp = app;
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + 1 for Agent Mode
        if ((e.ctrlKey || e.metaKey) && e.key === '1') {
            e.preventDefault();
            app.showMode('agent');
        }
        // Ctrl/Cmd + 2 for Chat Mode
        if ((e.ctrlKey || e.metaKey) && e.key === '2') {
            e.preventDefault();
            app.showMode('chat');
        }
        // Ctrl/Cmd + R to refresh logs (only in agent mode)
        if ((e.ctrlKey || e.metaKey) && e.key === 'r' && app.currentMode === 'agent') {
            e.preventDefault();
            app.loadAgentLogs();
        }
    });
    
    console.log('OpenManus Web Interface initialized successfully');
    console.log('Keyboard shortcuts: Ctrl+1 (Agent Mode), Ctrl+2 (Chat Mode), Ctrl+R (Refresh Logs)');
});
