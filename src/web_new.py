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
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        
        .header {
            background: linear-gradient(135deg, #0077b5, #005885);
            color: white;
            padding: 20px 0;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 5px;
        }
        
        .header p {
            opacity: 0.9;
        }
        
        .container {
            max-width: 1400px;
            margin: 30px auto;
            padding: 0 20px;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border: 1px solid #e1e5e9;
        }
        
        .card h2 {
            color: #0077b5;
            margin-bottom: 20px;
            font-size: 1.3em;
            border-bottom: 2px solid #f0f2f5;
            padding-bottom: 10px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #444;
        }
        
        .required {
            color: #e74c3c;
        }
        
        .form-group input, .form-group textarea, .form-group select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s ease;
            background: #fafbfc;
        }
        
        .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
            outline: none;
            border-color: #0077b5;
            background: white;
            box-shadow: 0 0 0 3px rgba(0, 119, 181, 0.1);
        }
        
        .btn {
            background: linear-gradient(135deg, #0077b5, #005885);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 119, 181, 0.3);
        }
        
        .btn:disabled {
            opacity: 0.6;
            transform: none;
            cursor: not-allowed;
        }
        
        .btn-success {
            background: linear-gradient(135deg, #28a745, #1e7e34);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #dc3545, #c82333);
        }
        
        .btn-small {
            padding: 8px 16px;
            font-size: 12px;
            width: auto;
            margin: 0 5px;
        }
        
        .contacts-grid {
            display: grid;
            gap: 15px;
        }
        
        .contact-card {
            background: white;
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .contact-card:hover {
            border-color: #0077b5;
            box-shadow: 0 4px 15px rgba(0, 119, 181, 0.1);
        }
        
        .contact-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        
        .contact-name {
            font-size: 1.2em;
            font-weight: 700;
            color: #333;
            margin-bottom: 4px;
        }
        
        .contact-company {
            color: #666;
            font-size: 0.9em;
        }
        
        .contact-reason {
            background: #f8f9fa;
            border-left: 4px solid #0077b5;
            padding: 12px 15px;
            margin: 15px 0;
            border-radius: 0 8px 8px 0;
            font-style: italic;
            color: #555;
        }
        
        .contact-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .status-badge {
            position: absolute;
            top: 15px;
            right: 15px;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .status-sent {
            background: #d4edda;
            color: #155724;
        }
        
        .status-pending {
            background: #fff3cd;
            color: #856404;
        }
        
        .message-area {
            margin-bottom: 20px;
        }
        
        .alert {
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 15px;
            border: 1px solid;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border-color: #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border-color: #f5c6cb;
        }
        
        .suggestions {
            margin-top: 20px;
        }
        
        .suggestion-item {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            position: relative;
        }
        
        .suggestion-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .suggestion-body {
            line-height: 1.6;
            color: #333;
            font-size: 15px;
        }
        
        .copy-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            transition: background 0.2s ease;
        }
        
        .copy-btn:hover {
            background: #218838;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #e1e5e9;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #0077b5;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #666;
        }
        
        .empty-state h3 {
            margin-bottom: 10px;
            color: #333;
        }
        
        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .contact-header {
                flex-direction: column;
            }
            
            .status-badge {
                position: static;
                align-self: flex-start;
                margin-top: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤝 LinkedIn Request Tracker</h1>
        <p>Track who you sent requests to and why • Generate follow-up messages</p>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="total-contacts">0</div>
                <div class="stat-label">Total Contacts</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="pending-contacts">0</div>
                <div class="stat-label">Pending Follow-ups</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="sent-messages">0</div>
                <div class="stat-label">Messages Sent</div>
            </div>
        </div>
        
        <div class="main-grid">
            <!-- Left Panel: Add New Contact -->
            <div class="card">
                <h2>📝 Add New LinkedIn Request</h2>
                
                <div id="message-area" class="message-area"></div>
                
                <form id="contact-form">
                    <div class="form-group">
                        <label for="name">Name <span class="required">*</span></label>
                        <input type="text" id="name" required placeholder="e.g., Ankit Muchhala">
                    </div>
                    
                    <div class="form-group">
                        <label for="company">Company</label>
                        <input type="text" id="company" placeholder="e.g., Amazon">
                    </div>
                    
                    <div class="form-group">
                        <label for="role">Role</label>
                        <input type="text" id="role" placeholder="e.g., Software Engineer">
                    </div>
                    
                    <div class="form-group">
                        <label for="request_reason">Why did you send the request? <span class="required">*</span></label>
                        <textarea id="request_reason" rows="3" required placeholder="e.g., referral at Amazon, met at tech meetup, alumni connection"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="linkedin_url">LinkedIn URL</label>
                        <input type="url" id="linkedin_url" placeholder="https://linkedin.com/in/ankitmuchhala">
                    </div>
                    
                    <button type="submit" class="btn">Add Contact</button>
                </form>
            </div>
            
            <!-- Right Panel: Contact List & Actions -->
            <div class="card">
                <h2>👥 Your LinkedIn Connections</h2>
                
                <div id="contacts-container" class="contacts-grid">
                    <div class="empty-state">
                        <h3>No contacts yet</h3>
                        <p>Add your first LinkedIn request to get started!</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Message Generation Modal (will be shown when Generate Message is clicked) -->
        <div id="message-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; border-radius: 12px; padding: 30px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2 id="modal-title">Generate Follow-up Message</h2>
                    <button onclick="closeModal()" style="background: none; border: none; font-size: 24px; cursor: pointer;">&times;</button>
                </div>
                
                <form id="message-form">
                    <div class="form-group">
                        <label for="tone">Message Tone</label>
                        <select id="tone">
                            <option value="friendly">Friendly</option>
                            <option value="direct">Direct</option>
                            <option value="formal">Formal</option>
                            <option value="warm">Warm</option>
                            <option value="playful">Playful</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="ask">What are you asking for?</label>
                        <input type="text" id="ask" value="a quick call to discuss opportunities" placeholder="e.g., referral help, coffee meeting, advice">
                    </div>
                    
                    <button type="submit" class="btn">Generate Messages</button>
                </form>
                
                <div id="generated-messages" class="suggestions"></div>
            </div>
        </div>
    </div>
    
    <script>
        let contacts = [];
        let currentContactId = null;
        
        // Load data on page load
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
            messagesDiv.innerHTML = '<div style="text-align: center; padding: 20px;">🤖 Generating messages...</div>';
            
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
                    messagesDiv.innerHTML = '<div class="alert alert-error">Error: ' + error.detail + '</div>';
                }
            } catch (error) {
                messagesDiv.innerHTML = '<div class="alert alert-error">Network error: ' + error.message + '</div>';
            }
        });
        
        async function loadContacts() {
            try {
                const response = await fetch('/api/contacts');
                contacts = await response.json();
                displayContacts(contacts);
            } catch (error) {
                console.error('Failed to load contacts:', error);
            }
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                document.getElementById('total-contacts').textContent = stats.total_contacts || 0;
                
                // Calculate pending and sent from contacts
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
                container.innerHTML = '<div class="empty-state"><h3>No contacts yet</h3><p>Add your first LinkedIn request to get started!</p></div>';
                return;
            }
            
            container.innerHTML = contacts.map(contact => `
                <div class="contact-card">
                    <div class="status-badge ${contact.message_sent ? 'status-sent' : 'status-pending'}">
                        ${contact.message_sent ? '✅ Sent' : '⏳ Pending'}
                    </div>
                    <div class="contact-header">
                        <div>
                            <div class="contact-name">${contact.name}</div>
                            <div class="contact-company">${contact.company || 'No company'} ${contact.role ? '• ' + contact.role : ''}</div>
                        </div>
                    </div>
                    <div class="contact-reason">
                        <strong>Reason:</strong> ${contact.request_reason || 'No reason provided'}
                    </div>
                    <div class="contact-actions">
                        <button class="btn btn-small" onclick="generateMessage(${contact.id}, '${contact.name}')">
                            💬 Generate Message
                        </button>
                        ${!contact.message_sent ? `<button class="btn btn-success btn-small" onclick="markAsSent(${contact.id})">✅ Mark as Sent</button>` : ''}
                        ${contact.linkedin_url ? `<a href="${contact.linkedin_url}" target="_blank" class="btn btn-small" style="text-decoration: none;">🔗 LinkedIn</a>` : ''}
                    </div>
                </div>
            `).join('');
        }
        
        function generateMessage(contactId, contactName) {
            currentContactId = contactId;
            document.getElementById('modal-title').textContent = `Generate Message for ${contactName}`;
            document.getElementById('message-modal').style.display = 'block';
            document.getElementById('generated-messages').innerHTML = '';
        }
        
        function closeModal() {
            document.getElementById('message-modal').style.display = 'none';
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
                <h3 style="margin-bottom: 15px;">Generated Messages</h3>
                <p style="margin-bottom: 20px; color: #666; font-size: 14px;">
                    <strong>Context:</strong> ${result.touchpoint.context || result.contact.request_reason}
                </p>
                ${result.messages.map(msg => `
                    <div class="suggestion-item">
                        <div class="suggestion-header">
                            <strong>Variant ${msg.variant} (${msg.tone})</strong>
                            <button class="copy-btn" onclick="copyMessage('${msg.body.replace(/'/g, "\\'")}')">📋 Copy</button>
                        </div>
                        <div class="suggestion-body">${msg.body}</div>
                        <div style="font-size: 12px; color: #999; margin-top: 8px;">${msg.body.length} characters</div>
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
            messageArea.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
            
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
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


def main():
    uvicorn.run(
        "src.web_new:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )


if __name__ == "__main__":
    main()