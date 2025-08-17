import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from .api import app as api_app

app = FastAPI(title="LinkedIn Follow-Up Assistant")

# Mount the API
app.mount("/api", api_app)

# Create static directory if it doesn't exist
static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Follow-Up Assistant</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
        }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.4em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }
        
        .form-group input, .form-group textarea, .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s ease;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.6;
            transform: none;
            cursor: not-allowed;
        }
        
        .contacts-list {
            max-height: 400px;
            overflow-y: auto;
            margin-top: 20px;
        }
        
        .contact-item {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .contact-item:hover {
            background: #e3f2fd;
            border-color: #667eea;
        }
        
        .contact-item.selected {
            background: #667eea;
            color: white;
            border-color: #5a67d8;
        }
        
        .contact-name {
            font-weight: 600;
            font-size: 16px;
        }
        
        .contact-company {
            color: #666;
            font-size: 14px;
            margin-top: 4px;
        }
        
        .contact-item.selected .contact-company {
            color: #e0e7ff;
        }
        
        .suggestions {
            margin-top: 20px;
        }
        
        .suggestion-item {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            position: relative;
        }
        
        .suggestion-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .suggestion-variant {
            font-weight: 600;
            color: #667eea;
        }
        
        .suggestion-tone {
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .suggestion-body {
            line-height: 1.6;
            color: #333;
        }
        
        .copy-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #28a745;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            transition: background 0.2s ease;
        }
        
        .copy-btn:hover {
            background: #218838;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 15px;
            border: 1px solid #f5c6cb;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 15px;
            border: 1px solid #c3e6cb;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin-bottom: 20px;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #666;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤝 LinkedIn Follow-Up Assistant</h1>
            <p>Generate personalized follow-up messages for your professional network</p>
        </div>
        
        <div class="main-content">
            <!-- Left Panel: Add Contacts & Context -->
            <div class="card">
                <h2>📝 Add Contact & Context</h2>
                
                <div id="stats" class="stats">
                    <div class="stat">
                        <div class="stat-number" id="contact-count">0</div>
                        <div class="stat-label">Contacts</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number" id="message-count">0</div>
                        <div class="stat-label">Messages</div>
                    </div>
                </div>
                
                <div id="message-area"></div>
                
                <form id="contact-form">
                    <div class="form-group">
                        <label for="name">Name *</label>
                        <input type="text" id="name" required placeholder="e.g., Sarah Chen">
                    </div>
                    
                    <div class="form-group">
                        <label for="company">Company</label>
                        <input type="text" id="company" placeholder="e.g., DataFlow Analytics">
                    </div>
                    
                    <div class="form-group">
                        <label for="role">Role</label>
                        <input type="text" id="role" placeholder="e.g., VP Engineering">
                    </div>
                    
                    <div class="form-group">
                        <label for="linkedin_url">LinkedIn URL</label>
                        <input type="url" id="linkedin_url" placeholder="e.g., linkedin.com/in/sarahchen">
                    </div>
                    
                    <div class="form-group">
                        <label for="tags">Tags</label>
                        <input type="text" id="tags" placeholder="e.g., ai,startup,hiring">
                    </div>
                    
                    <button type="submit" class="btn">Add Contact</button>
                </form>
                
                <form id="context-form" style="margin-top: 30px;">
                    <div class="form-group">
                        <label for="context">Connection Context *</label>
                        <textarea id="context" rows="3" required placeholder="e.g., met at AI Summit 2024, discussed real-time data pipelines"></textarea>
                    </div>
                    
                    <button type="submit" class="btn">Add Context</button>
                </form>
            </div>
            
            <!-- Right Panel: Generate Messages -->
            <div class="card">
                <h2>💬 Generate Follow-ups</h2>
                
                <div class="form-group">
                    <label>Select Contact</label>
                    <div class="contacts-list" id="contacts-list">
                        <div class="loading">Loading contacts...</div>
                    </div>
                </div>
                
                <form id="suggest-form">
                    <div class="form-group">
                        <label for="tone">Tone</label>
                        <select id="tone">
                            <option value="friendly">Friendly</option>
                            <option value="direct">Direct</option>
                            <option value="formal">Formal</option>
                            <option value="warm">Warm</option>
                            <option value="playful">Playful</option>
                            <option value="short-n-sweet">Short & Sweet</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="ask">What are you asking for?</label>
                        <input type="text" id="ask" value="a quick 15-min call" placeholder="e.g., a coffee meeting next week">
                    </div>
                    
                    <button type="submit" class="btn" disabled>Generate Suggestions</button>
                </form>
                
                <div id="suggestions" class="suggestions"></div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedContactId = null;
        let contacts = [];
        
        // Load initial data
        document.addEventListener('DOMContentLoaded', function() {
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
                linkedin_url: document.getElementById('linkedin_url').value,
                tags: document.getElementById('tags').value
            };
            
            try {
                const response = await fetch('/api/contacts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    const contact = await response.json();
                    showMessage('Contact added successfully!', 'success');
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
        
        // Context form submission
        document.getElementById('context-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!selectedContactId) {
                showMessage('Please select a contact first', 'error');
                return;
            }
            
            const formData = {
                contact_id: selectedContactId,
                context: document.getElementById('context').value
            };
            
            try {
                const response = await fetch('/api/touchpoints', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    const touchpoint = await response.json();
                    showMessage('Context added successfully!', 'success');
                    document.getElementById('context').value = '';
                    loadContacts();
                } else {
                    const error = await response.json();
                    showMessage('Error: ' + error.detail, 'error');
                }
            } catch (error) {
                showMessage('Network error: ' + error.message, 'error');
            }
        });
        
        // Suggest form submission
        document.getElementById('suggest-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!selectedContactId) {
                showMessage('Please select a contact first', 'error');
                return;
            }
            
            const formData = {
                contact_id: selectedContactId,
                tone: document.getElementById('tone').value,
                ask: document.getElementById('ask').value
            };
            
            const suggestionsDiv = document.getElementById('suggestions');
            suggestionsDiv.innerHTML = '<div class="loading">Generating suggestions...</div>';
            
            try {
                const response = await fetch('/api/suggest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    displaySuggestions(result);
                    loadStats();
                } else {
                    const error = await response.json();
                    suggestionsDiv.innerHTML = '';
                    showMessage('Error: ' + error.detail, 'error');
                }
            } catch (error) {
                suggestionsDiv.innerHTML = '';
                showMessage('Network error: ' + error.message, 'error');
            }
        });
        
        async function loadContacts() {
            try {
                const response = await fetch('/api/contacts');
                contacts = await response.json();
                displayContacts(contacts);
            } catch (error) {
                document.getElementById('contacts-list').innerHTML = '<div class="error">Failed to load contacts</div>';
            }
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                document.getElementById('contact-count').textContent = stats.total_contacts;
                document.getElementById('message-count').textContent = stats.total_messages;
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }
        
        function displayContacts(contacts) {
            const contactsList = document.getElementById('contacts-list');
            
            if (contacts.length === 0) {
                contactsList.innerHTML = '<div class="loading">No contacts yet. Add your first contact!</div>';
                return;
            }
            
            contactsList.innerHTML = contacts.map(contact => `
                <div class="contact-item" onclick="selectContact(${contact.id})">
                    <div class="contact-name">${contact.name}</div>
                    <div class="contact-company">${contact.company || 'No company'} • ${contact.touchpoint_count} contexts</div>
                </div>
            `).join('');
        }
        
        function selectContact(contactId) {
            selectedContactId = contactId;
            
            // Update UI
            document.querySelectorAll('.contact-item').forEach(item => item.classList.remove('selected'));
            event.target.closest('.contact-item').classList.add('selected');
            
            // Enable suggest form
            document.querySelector('#suggest-form button').disabled = false;
            
            // Clear previous suggestions
            document.getElementById('suggestions').innerHTML = '';
        }
        
        function displaySuggestions(result) {
            const suggestionsDiv = document.getElementById('suggestions');
            
            const html = `
                <h3>Follow-up suggestions for ${result.contact.name}</h3>
                <p style="margin-bottom: 20px; color: #666; font-size: 14px;">
                    Context: ${result.touchpoint.context.substring(0, 100)}${result.touchpoint.context.length > 100 ? '...' : ''}
                </p>
                ${result.messages.map(msg => `
                    <div class="suggestion-item">
                        <button class="copy-btn" onclick="copyToClipboard('${msg.body.replace(/'/g, "\\'")}')">Copy</button>
                        <div class="suggestion-header">
                            <span class="suggestion-variant">Variant ${msg.variant}</span>
                            <span class="suggestion-tone">${msg.tone}</span>
                        </div>
                        <div class="suggestion-body">${msg.body}</div>
                        <div style="font-size: 12px; color: #999; margin-top: 8px;">${msg.body.length} characters</div>
                    </div>
                `).join('')}
            `;
            
            suggestionsDiv.innerHTML = html;
        }
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showMessage('Message copied to clipboard!', 'success');
            }).catch(() => {
                showMessage('Failed to copy message', 'error');
            });
        }
        
        function showMessage(message, type) {
            const messageArea = document.getElementById('message-area');
            messageArea.innerHTML = `<div class="${type}">${message}</div>`;
            
            setTimeout(() => {
                messageArea.innerHTML = '';
            }, 5000);
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


def main():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "src.web:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )


if __name__ == "__main__":
    main()