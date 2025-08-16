import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from .api import app as api_app

app = FastAPI(title="LinkedIn Request Tracker")

# Mount the API
app.mount("/api", api_app)

@app.get("/", response_class=HTMLResponse)
async def get_index():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Request Tracker</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #ec4899;
            --accent: #06b6d4;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            
            /* Light mode */
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #f1f5f9;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --border-light: #f1f5f9;
            --shadow: rgba(15, 23, 42, 0.08);
            --shadow-lg: rgba(15, 23, 42, 0.15);
        }
        
        [data-theme="dark"] {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --border: #334155;
            --border-light: #475569;
            --shadow: rgba(0, 0, 0, 0.3);
            --shadow-lg: rgba(0, 0, 0, 0.5);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.6;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .navbar {
            background: var(--bg-primary);
            border-bottom: 1px solid var(--border);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 50;
            backdrop-filter: blur(8px);
        }
        
        .navbar-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 700;
            font-size: 1.25rem;
            color: var(--primary);
        }
        
        .logo i {
            font-size: 1.5rem;
        }
        
        .navbar-actions {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .theme-toggle {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 50px;
            padding: 0.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            min-width: 3rem;
            height: 3rem;
            justify-content: center;
        }
        
        .theme-toggle:hover {
            background: var(--bg-primary);
            border-color: var(--primary);
            transform: scale(1.05);
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 40px var(--shadow-lg);
            border-color: var(--primary);
        }
        
        .stat-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }
        
        .stat-label {
            color: var(--text-muted);
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 400px 1fr;
            gap: 2rem;
            align-items: start;
        }
        
        .card {
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 4px 20px var(--shadow);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            box-shadow: 0 8px 40px var(--shadow-lg);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-light);
        }
        
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .card-icon {
            font-size: 1.25rem;
            color: var(--primary);
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }
        
        .required {
            color: var(--error);
        }
        
        .form-input, .form-textarea, .form-select {
            width: 100%;
            padding: 0.875rem 1rem;
            border: 2px solid var(--border);
            border-radius: 12px;
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-size: 0.875rem;
            transition: all 0.3s ease;
            font-family: inherit;
        }
        
        .form-input:focus, .form-textarea:focus, .form-select:focus {
            outline: none;
            border-color: var(--primary);
            background: var(--bg-primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
            transform: translateY(-1px);
        }
        
        .form-textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.875rem 1.5rem;
            border: none;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            font-family: inherit;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--success), #059669);
            color: white;
        }
        
        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
        }
        
        .btn-secondary {
            background: var(--bg-tertiary);
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }
        
        .btn-secondary:hover {
            background: var(--bg-primary);
            color: var(--text-primary);
            border-color: var(--primary);
        }
        
        .btn-small {
            padding: 0.5rem 1rem;
            font-size: 0.75rem;
        }
        
        .btn-full {
            width: 100%;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none !important;
        }
        
        .contacts-grid {
            display: grid;
            gap: 1.5rem;
        }
        
        .contact-card {
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .contact-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(180deg, var(--primary), var(--secondary));
            transition: all 0.3s ease;
        }
        
        .contact-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 30px var(--shadow-lg);
            border-color: var(--primary);
        }
        
        .contact-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }
        
        .contact-info h3 {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }
        
        .contact-meta {
            color: var(--text-muted);
            font-size: 0.875rem;
        }
        
        .status-badge {
            padding: 0.375rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .status-sent {
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.2);
        }
        
        .status-pending {
            background: rgba(245, 158, 11, 0.1);
            color: var(--warning);
            border: 1px solid rgba(245, 158, 11, 0.2);
        }
        
        .contact-reason {
            background: var(--bg-secondary);
            border: 1px solid var(--border-light);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            font-style: italic;
            color: var(--text-secondary);
            position: relative;
            overflow: hidden;
        }
        
        .contact-reason::before {
            content: '"';
            position: absolute;
            top: -0.5rem;
            left: 0.5rem;
            font-size: 3rem;
            color: var(--primary);
            opacity: 0.2;
        }
        
        .contact-actions {
            display: flex;
            gap: 0.75rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }
        
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(4px);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }
        
        .modal.active {
            opacity: 1;
            visibility: visible;
        }
        
        .modal-content {
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 2rem;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            transform: scale(0.9) translateY(20px);
            transition: all 0.3s ease;
        }
        
        .modal.active .modal-content {
            transform: scale(1) translateY(0);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-light);
        }
        
        .modal-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            color: var(--text-muted);
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .modal-close:hover {
            background: var(--bg-secondary);
            color: var(--text-primary);
        }
        
        .suggestions {
            margin-top: 1.5rem;
        }
        
        .suggestion-item {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            position: relative;
            transition: all 0.3s ease;
        }
        
        .suggestion-item:hover {
            border-color: var(--primary);
            box-shadow: 0 4px 15px var(--shadow);
        }
        
        .suggestion-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .suggestion-variant {
            font-weight: 600;
            color: var(--primary);
        }
        
        .suggestion-body {
            line-height: 1.6;
            color: var(--text-primary);
            margin-bottom: 0.75rem;
        }
        
        .suggestion-meta {
            font-size: 0.75rem;
            color: var(--text-muted);
        }
        
        .copy-btn {
            background: var(--success);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .copy-btn:hover {
            background: #059669;
            transform: scale(1.05);
        }
        
        .alert {
            padding: 1rem 1.25rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .alert-success {
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.2);
        }
        
        .alert-error {
            background: rgba(239, 68, 68, 0.1);
            color: var(--error);
            border: 1px solid rgba(239, 68, 68, 0.2);
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem 2rem;
            color: var(--text-muted);
        }
        
        .empty-state i {
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }
        
        .empty-state h3 {
            margin-bottom: 0.5rem;
            color: var(--text-secondary);
        }
        
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 2rem;
            color: var(--text-muted);
        }
        
        .spinner {
            width: 1rem;
            height: 1rem;
            border: 2px solid var(--border);
            border-top: 2px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .contact-actions {
                flex-direction: column;
            }
            
            .container {
                padding: 1rem;
            }
            
            .card {
                padding: 1.5rem;
            }
        }
        
        /* Smooth scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-muted);
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-content">
            <div class="logo">
                <i class="fab fa-linkedin"></i>
                <span>Request Tracker</span>
            </div>
            <div class="navbar-actions">
                <button class="theme-toggle" onclick="toggleTheme()">
                    <i class="fas fa-sun" id="theme-icon"></i>
                </button>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-users"></i>
                </div>
                <div class="stat-number" id="total-contacts">0</div>
                <div class="stat-label">Total Contacts</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-clock"></i>
                </div>
                <div class="stat-number" id="pending-contacts">0</div>
                <div class="stat-label">Pending Follow-ups</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-paper-plane"></i>
                </div>
                <div class="stat-number" id="sent-messages">0</div>
                <div class="stat-label">Messages Sent</div>
            </div>
        </div>
        
        <div class="main-grid">
            <div class="card">
                <div class="card-header">
                    <i class="card-icon fas fa-plus"></i>
                    <h2 class="card-title">Add New Request</h2>
                </div>
                
                <div id="message-area"></div>
                
                <form id="contact-form">
                    <div class="form-group">
                        <label class="form-label" for="name">Full Name <span class="required">*</span></label>
                        <input type="text" id="name" class="form-input" required placeholder="e.g., Ankit Muchhala">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="company">Company</label>
                        <input type="text" id="company" class="form-input" placeholder="e.g., Amazon">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="role">Job Title</label>
                        <input type="text" id="role" class="form-input" placeholder="e.g., Software Engineer">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="request_reason">Why did you send the request? <span class="required">*</span></label>
                        <textarea id="request_reason" class="form-textarea" required placeholder="e.g., referral at Amazon for SDE role, alumni connection, met at tech meetup"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="linkedin_url">LinkedIn Profile</label>
                        <input type="url" id="linkedin_url" class="form-input" placeholder="https://linkedin.com/in/ankitmuchhala">
                    </div>
                    
                    <button type="submit" class="btn btn-primary btn-full">
                        <i class="fas fa-plus"></i>
                        Add Contact
                    </button>
                </form>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <i class="card-icon fas fa-address-book"></i>
                    <h2 class="card-title">Your Connections</h2>
                </div>
                
                <div id="contacts-container" class="contacts-grid">
                    <div class="loading">
                        <div class="spinner"></div>
                        Loading contacts...
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Message Generation Modal -->
    <div id="message-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modal-title">Generate Follow-up Message</h2>
                <button class="modal-close" onclick="closeModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <form id="message-form">
                <div class="form-group">
                    <label class="form-label" for="tone">Message Tone</label>
                    <select id="tone" class="form-select">
                        <option value="friendly">😊 Friendly</option>
                        <option value="direct">📋 Direct</option>
                        <option value="formal">🎩 Formal</option>
                        <option value="warm">🤗 Warm</option>
                        <option value="playful">😄 Playful</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="ask">What are you asking for?</label>
                    <input type="text" id="ask" class="form-input" value="a quick call to discuss opportunities" placeholder="e.g., referral help, coffee meeting, advice">
                </div>
                
                <button type="submit" class="btn btn-primary btn-full">
                    <i class="fas fa-magic"></i>
                    Generate Messages
                </button>
            </form>
            
            <div id="generated-messages" class="suggestions"></div>
        </div>
    </div>
    
    <script>
        let contacts = [];
        let currentContactId = null;
        
        // Theme management
        function initTheme() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            updateThemeIcon(savedTheme);
        }
        
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        }
        
        function updateThemeIcon(theme) {
            const icon = document.getElementById('theme-icon');
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            initTheme();
            loadContacts();
            loadStats();
        });
        
        // Contact form submission
        document.getElementById('contact-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('name').value,
                company: document.getElementById('company').value,
                role: document.getElementById('role').value,
                request_reason: document.getElementById('request_reason').value,
                linkedin_url: document.getElementById('linkedin_url').value
            };
            
            try {
                const response = await fetch('/api/contacts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    showMessage('Contact added successfully! 🎉', 'success');
                    document.getElementById('contact-form').reset();
                    loadContacts();
                    loadStats();
                } else {
                    const error = await response.json();
                    showMessage('Error: ' + error.detail, 'error');
                }
            } catch (error) {
                showMessage('Network error: ' + error.message, 'error');
            }
        });
        
        // Message form submission
        document.getElementById('message-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!currentContactId) return;
            
            const formData = {
                contact_id: currentContactId,
                tone: document.getElementById('tone').value,
                ask: document.getElementById('ask').value
            };
            
            const messagesDiv = document.getElementById('generated-messages');
            messagesDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Generating messages with AI...</div>';
            
            try {
                const response = await fetch('/api/suggest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    displayMessages(result);
                } else {
                    const error = await response.json();
                    messagesDiv.innerHTML = '<div class="alert alert-error"><i class="fas fa-exclamation-triangle"></i>Error: ' + error.detail + '</div>';
                }
            } catch (error) {
                messagesDiv.innerHTML = '<div class="alert alert-error"><i class="fas fa-exclamation-triangle"></i>Network error: ' + error.message + '</div>';
            }
        });
        
        async function loadContacts() {
            try {
                const response = await fetch('/api/contacts');
                contacts = await response.json();
                displayContacts(contacts);
            } catch (error) {
                console.error('Failed to load contacts:', error);
                document.getElementById('contacts-container').innerHTML = 
                    '<div class="alert alert-error"><i class="fas fa-exclamation-triangle"></i>Failed to load contacts</div>';
            }
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                document.getElementById('total-contacts').textContent = stats.total_contacts || 0;
                
                const pending = contacts.filter(c => !c.message_sent).length;
                const sent = contacts.filter(c => c.message_sent).length;
                document.getElementById('pending-contacts').textContent = pending;
                document.getElementById('sent-messages').textContent = sent;
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }
        
        function displayContacts(contacts) {
            const container = document.getElementById('contacts-container');
            
            if (contacts.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-users"></i>
                        <h3>No contacts yet</h3>
                        <p>Add your first LinkedIn request to get started!</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = contacts.map(contact => `
                <div class="contact-card">
                    <div class="contact-header">
                        <div class="contact-info">
                            <h3>${contact.name}</h3>
                            <div class="contact-meta">
                                ${contact.company || 'No company'} ${contact.role ? '• ' + contact.role : ''}
                            </div>
                        </div>
                        <div class="status-badge ${contact.message_sent ? 'status-sent' : 'status-pending'}">
                            <i class="fas ${contact.message_sent ? 'fa-check' : 'fa-clock'}"></i>
                            ${contact.message_sent ? 'Sent' : 'Pending'}
                        </div>
                    </div>
                    
                    ${contact.request_reason ? `
                        <div class="contact-reason">
                            ${contact.request_reason}
                        </div>
                    ` : ''}
                    
                    <div class="contact-actions">
                        <button class="btn btn-primary btn-small" onclick="generateMessage(${contact.id}, '${contact.name.replace(/'/g, "\\'")}')">
                            <i class="fas fa-comment"></i>
                            Generate Message
                        </button>
                        ${!contact.message_sent ? `
                            <button class="btn btn-success btn-small" onclick="markAsSent(${contact.id})">
                                <i class="fas fa-check"></i>
                                Mark as Sent
                            </button>
                        ` : ''}
                        ${contact.linkedin_url ? `
                            <a href="${contact.linkedin_url}" target="_blank" class="btn btn-secondary btn-small">
                                <i class="fab fa-linkedin"></i>
                                LinkedIn
                            </a>
                        ` : ''}
                    </div>
                </div>
            `).join('');
        }
        
        function generateMessage(contactId, contactName) {
            currentContactId = contactId;
            document.getElementById('modal-title').textContent = `Generate Message for ${contactName}`;
            document.getElementById('message-modal').classList.add('active');
            document.getElementById('generated-messages').innerHTML = '';
        }
        
        function closeModal() {
            document.getElementById('message-modal').classList.remove('active');
            currentContactId = null;
        }
        
        async function markAsSent(contactId) {
            try {
                const response = await fetch(`/api/contacts/${contactId}/mark-sent`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    showMessage('Marked as sent! ✅', 'success');
                    loadContacts();
                    loadStats();
                } else {
                    showMessage('Failed to mark as sent', 'error');
                }
            } catch (error) {
                showMessage('Network error: ' + error.message, 'error');
            }
        }
        
        function displayMessages(result) {
            const html = `
                <h3 style="margin-bottom: 1rem; color: var(--text-primary);">
                    <i class="fas fa-magic" style="color: var(--primary); margin-right: 0.5rem;"></i>
                    Generated Messages
                </h3>
                <p style="margin-bottom: 1.5rem; color: var(--text-muted); font-size: 0.875rem;">
                    <strong>Context:</strong> ${result.touchpoint?.context || result.contact.request_reason || 'No context available'}
                </p>
                ${result.messages.map(msg => `
                    <div class="suggestion-item">
                        <div class="suggestion-header">
                            <span class="suggestion-variant">
                                <i class="fas fa-comment-dots"></i>
                                Variant ${msg.variant} (${msg.tone})
                            </span>
                            <button class="copy-btn" onclick="copyMessage('${msg.body.replace(/'/g, "\\'")}')">
                                <i class="fas fa-copy"></i>
                                Copy
                            </button>
                        </div>
                        <div class="suggestion-body">${msg.body}</div>
                        <div class="suggestion-meta">
                            <i class="fas fa-font"></i>
                            ${msg.body.length} characters
                        </div>
                    </div>
                `).join('')}
            `;
            
            document.getElementById('generated-messages').innerHTML = html;
        }
        
        function copyMessage(text) {
            navigator.clipboard.writeText(text).then(() => {
                showMessage('Message copied to clipboard! 📋', 'success');
            }).catch(() => {
                showMessage('Failed to copy message', 'error');
            });
        }
        
        function showMessage(message, type) {
            const messageArea = document.getElementById('message-area');
            const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';
            messageArea.innerHTML = `<div class="alert alert-${type}"><i class="fas ${icon}"></i>${message}</div>`;
            
            setTimeout(() => {
                messageArea.innerHTML = '';
            }, 5000);
        }
        
        // Close modal when clicking outside
        document.getElementById('message-modal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeModal();
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                toggleTheme();
            }
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


def main():
    uvicorn.run(
        "src.web_modern:app",
        host="127.0.0.1",
        port=8002,
        reload=True
    )


if __name__ == "__main__":
    main()