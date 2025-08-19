// Content script for job portal field detection and auto-filling
class JobPortalAssistant {
  constructor() {
    this.isEnabled = false;
    this.resumeData = null;
    this.currentPlatform = this.detectPlatform();
    this.fieldSelectors = this.getFieldSelectors();
    
    // Initialize the assistant
    this.init();
  }

  init() {
    // Load settings from storage
    this.loadSettings();
    
    // Add visual indicators
    this.addFloatingButton();
    
    // Listen for messages from popup
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      this.handleMessage(request, sender, sendResponse);
      return true;
    });

    // Monitor for dynamic content changes
    this.observeDOMChanges();
  }

  detectPlatform() {
    const hostname = window.location.hostname.toLowerCase();
    const pathname = window.location.pathname.toLowerCase();
    
    if (hostname.includes('linkedin.com')) {
      if (pathname.includes('/jobs/') || document.querySelector('.jobs-apply-form')) {
        return 'linkedin';
      }
    } else if (hostname.includes('simplify.jobs')) {
      return 'simplify';
    } else if (hostname.includes('jobrightai.com')) {
      return 'jobrightai';
    } else if (this.detectGenericJobForm()) {
      return 'generic';
    }
    
    return 'unknown';
  }

  detectGenericJobForm() {
    // Look for common job application form indicators
    const indicators = [
      'input[name*="name"]',
      'input[name*="email"]',
      'input[name*="phone"]',
      'textarea[name*="cover"]',
      'input[type="file"]',
      '.application-form',
      '.job-application',
      '.apply-form'
    ];
    
    return indicators.some(selector => document.querySelector(selector));
  }

  getFieldSelectors() {
    const selectors = {
      linkedin: {
        firstName: 'input[name="firstName"], input[id*="first"], input[placeholder*="First"]',
        lastName: 'input[name="lastName"], input[id*="last"], input[placeholder*="Last"]',
        email: 'input[name="email"], input[type="email"]',
        phone: 'input[name="phone"], input[type="tel"], input[placeholder*="phone"]',
        coverLetter: 'textarea[name="coverLetter"], textarea[placeholder*="cover"], .jobs-apply-form textarea',
        resume: 'input[type="file"][name*="resume"], input[type="file"][accept*=".pdf"]',
        linkedinProfile: 'input[name="linkedinProfile"], input[placeholder*="linkedin"]',
        location: 'input[name="location"], input[placeholder*="location"], input[placeholder*="city"]',
        experience: 'select[name*="experience"], input[name*="experience"]',
        education: 'input[name*="education"], select[name*="education"]',
        company: 'input[name*="company"], input[placeholder*="company"]',
        position: 'input[name*="position"], input[placeholder*="title"], input[name*="title"]',
        salary: 'input[name*="salary"], input[placeholder*="salary"]'
      },
      simplify: {
        firstName: 'input[name="firstName"], #firstName, input[placeholder*="first" i]',
        lastName: 'input[name="lastName"], #lastName, input[placeholder*="last" i]',
        email: 'input[name="email"], input[type="email"], #email',
        phone: 'input[name="phone"], input[type="tel"], #phone',
        coverLetter: 'textarea[name*="cover"], #coverLetter, textarea[placeholder*="cover" i]',
        resume: 'input[type="file"]',
        location: 'input[name*="location"], #location',
        experience: 'input[name*="experience"], select[name*="experience"]',
        linkedinProfile: 'input[name*="linkedin"], input[placeholder*="linkedin" i]'
      },
      jobrightai: {
        firstName: 'input[name="first_name"], input[id="first_name"]',
        lastName: 'input[name="last_name"], input[id="last_name"]',
        email: 'input[name="email"], input[type="email"]',
        phone: 'input[name="phone"], input[type="tel"]',
        coverLetter: 'textarea[name="cover_letter"], textarea[name="message"]',
        resume: 'input[type="file"][name="resume"]',
        location: 'input[name="location"]',
        experience: 'select[name="experience_level"]'
      },
      generic: {
        firstName: 'input[name*="first" i], input[id*="first" i], input[placeholder*="first" i]',
        lastName: 'input[name*="last" i], input[id*="last" i], input[placeholder*="last" i]',
        fullName: 'input[name*="name" i]:not([name*="first"]):not([name*="last"]), input[placeholder*="full name" i]',
        email: 'input[name*="email" i], input[type="email"]',
        phone: 'input[name*="phone" i], input[type="tel"], input[placeholder*="phone" i]',
        coverLetter: 'textarea[name*="cover" i], textarea[name*="message" i], textarea[placeholder*="cover" i]',
        resume: 'input[type="file"], input[name*="resume" i], input[accept*="pdf"]',
        location: 'input[name*="location" i], input[name*="city" i], input[placeholder*="location" i]',
        experience: 'select[name*="experience" i], input[name*="experience" i]',
        company: 'input[name*="company" i], input[placeholder*="company" i]',
        position: 'input[name*="position" i], input[name*="title" i], input[placeholder*="title" i]'
      }
    };

    return selectors[this.currentPlatform] || selectors.generic;
  }

  addFloatingButton() {
    if (document.getElementById('linkedin-assistant-btn')) return;

    const button = document.createElement('div');
    button.id = 'linkedin-assistant-btn';
    button.innerHTML = '🤖';
    button.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      width: 50px;
      height: 50px;
      background: #0066cc;
      color: white;
      border: none;
      border-radius: 50%;
      font-size: 24px;
      cursor: pointer;
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(0,102,204,0.3);
      transition: all 0.3s ease;
    `;

    button.addEventListener('mouseenter', () => {
      button.style.transform = 'scale(1.1)';
      button.style.boxShadow = '0 6px 20px rgba(0,102,204,0.4)';
    });

    button.addEventListener('mouseleave', () => {
      button.style.transform = 'scale(1)';
      button.style.boxShadow = '0 4px 12px rgba(0,102,204,0.3)';
    });

    button.addEventListener('click', () => {
      this.showQuickActions();
    });

    document.body.appendChild(button);
  }

  showQuickActions() {
    // Remove existing menu
    const existingMenu = document.getElementById('assistant-quick-menu');
    if (existingMenu) existingMenu.remove();

    const menu = document.createElement('div');
    menu.id = 'assistant-quick-menu';
    menu.style.cssText = `
      position: fixed;
      top: 80px;
      right: 20px;
      width: 250px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.15);
      z-index: 10001;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      border: 1px solid #e0e0e0;
    `;

    const actions = [
      { text: '🔍 Analyze Fields', action: 'analyzeFields' },
      { text: '🚀 Auto-Fill Form', action: 'fillFields' },
      { text: '📋 Extract Job Info', action: 'extractJobInfo' },
      { text: '💼 Generate Cover Letter', action: 'generateCoverLetter' },
      { text: '⚙️ Settings', action: 'openSettings' }
    ];

    actions.forEach((item, index) => {
      const btn = document.createElement('button');
      btn.textContent = item.text;
      btn.style.cssText = `
        width: 100%;
        padding: 12px 16px;
        border: none;
        background: transparent;
        text-align: left;
        cursor: pointer;
        font-size: 14px;
        border-radius: ${index === 0 ? '8px 8px 0 0' : index === actions.length - 1 ? '0 0 8px 8px' : '0'};
        border-bottom: ${index < actions.length - 1 ? '1px solid #f0f0f0' : 'none'};
      `;

      btn.addEventListener('mouseenter', () => {
        btn.style.background = '#f8f9fa';
      });

      btn.addEventListener('mouseleave', () => {
        btn.style.background = 'transparent';
      });

      btn.addEventListener('click', () => {
        this.executeAction(item.action);
        menu.remove();
      });

      menu.appendChild(btn);
    });

    // Close menu when clicking outside
    const closeMenu = (e) => {
      if (!menu.contains(e.target) && e.target.id !== 'linkedin-assistant-btn') {
        menu.remove();
        document.removeEventListener('click', closeMenu);
      }
    };

    setTimeout(() => {
      document.addEventListener('click', closeMenu);
    }, 100);

    document.body.appendChild(menu);
  }

  executeAction(action) {
    switch (action) {
      case 'analyzeFields':
        this.analyzeCurrentFields();
        break;
      case 'fillFields':
        this.fillApplicationFields();
        break;
      case 'extractJobInfo':
        this.extractJobInformation();
        break;
      case 'generateCoverLetter':
        this.generateCoverLetter();
        break;
      case 'openSettings':
        chrome.runtime.sendMessage({ action: 'openPopup' });
        break;
    }
  }

  analyzeCurrentFields() {
    const fields = this.findAllFormFields();
    const analysis = {
      platform: this.currentPlatform,
      fieldsFound: fields.length,
      fields: fields.map(field => ({
        type: this.classifyField(field),
        element: field.tagName.toLowerCase(),
        name: field.name || field.id,
        placeholder: field.placeholder,
        required: field.required
      }))
    };

    this.showNotification(`Found ${fields.length} form fields on ${this.currentPlatform} platform`, 'info');
    console.log('Field Analysis:', analysis);

    // Send to popup if open
    chrome.runtime.sendMessage({
      action: 'fieldAnalysis',
      data: analysis
    });
  }

  findAllFormFields() {
    const formFields = document.querySelectorAll('input, textarea, select');
    return Array.from(formFields).filter(field => {
      // Filter out hidden fields, buttons, etc.
      return !(['hidden', 'submit', 'button', 'reset'].includes(field.type)) &&
             field.style.display !== 'none' &&
             field.offsetParent !== null;
    });
  }

  classifyField(field) {
    const name = (field.name || field.id || '').toLowerCase();
    const placeholder = (field.placeholder || '').toLowerCase();
    const combined = `${name} ${placeholder}`.toLowerCase();

    if (combined.includes('first') && combined.includes('name')) return 'firstName';
    if (combined.includes('last') && combined.includes('name')) return 'lastName';
    if (combined.includes('email')) return 'email';
    if (combined.includes('phone')) return 'phone';
    if (combined.includes('cover') && combined.includes('letter')) return 'coverLetter';
    if (combined.includes('location') || combined.includes('city')) return 'location';
    if (combined.includes('experience')) return 'experience';
    if (combined.includes('linkedin')) return 'linkedinProfile';
    if (combined.includes('company')) return 'company';
    if (combined.includes('salary')) return 'salary';
    if (field.type === 'file') return 'resume';
    if (field.tagName === 'TEXTAREA') return 'textArea';

    return 'unknown';
  }

  async fillApplicationFields() {
    if (!this.resumeData) {
      this.showNotification('Please add your resume data in the extension settings first', 'error');
      return;
    }

    const personalInfo = await this.extractPersonalInfo(this.resumeData);
    let filledCount = 0;

    // Fill each field type
    for (const [fieldType, selector] of Object.entries(this.fieldSelectors)) {
      const elements = document.querySelectorAll(selector);
      elements.forEach(element => {
        const value = this.getFieldValue(fieldType, personalInfo);
        if (value && this.fillField(element, value)) {
          filledCount++;
        }
      });
    }

    this.showNotification(`Auto-filled ${filledCount} fields`, filledCount > 0 ? 'success' : 'warning');
  }

  getFieldValue(fieldType, personalInfo) {
    const mapping = {
      firstName: personalInfo.firstName,
      lastName: personalInfo.lastName,
      email: personalInfo.email,
      phone: personalInfo.phone,
      location: personalInfo.location,
      linkedinProfile: personalInfo.linkedin,
      company: personalInfo.currentCompany,
      position: personalInfo.currentPosition,
      experience: personalInfo.yearsExperience,
      education: personalInfo.education
    };

    return mapping[fieldType] || null;
  }

  fillField(element, value) {
    if (!element || !value) return false;

    try {
      // Handle different input types
      if (element.type === 'checkbox' || element.type === 'radio') {
        element.checked = Boolean(value);
      } else if (element.tagName === 'SELECT') {
        // Try to find matching option
        const options = Array.from(element.options);
        const match = options.find(opt => 
          opt.value.toLowerCase().includes(value.toString().toLowerCase()) ||
          opt.text.toLowerCase().includes(value.toString().toLowerCase())
        );
        if (match) {
          element.value = match.value;
        }
      } else {
        element.value = value;
      }

      // Trigger change events
      element.dispatchEvent(new Event('input', { bubbles: true }));
      element.dispatchEvent(new Event('change', { bubbles: true }));
      element.dispatchEvent(new Event('blur', { bubbles: true }));

      // Add visual feedback
      this.highlightField(element);

      return true;
    } catch (error) {
      console.error('Error filling field:', error);
      return false;
    }
  }

  highlightField(element) {
    const originalBorder = element.style.border;
    element.style.border = '2px solid #4CAF50';
    element.style.boxShadow = '0 0 8px rgba(76, 175, 80, 0.3)';

    setTimeout(() => {
      element.style.border = originalBorder;
      element.style.boxShadow = '';
    }, 2000);
  }

  async extractPersonalInfo(resumeText) {
    // Use AI to extract structured data from resume
    try {
      const apiKey = await this.getStoredApiKey();
      if (!apiKey) {
        throw new Error('DeepSeek API key not configured');
      }

      const response = await this.callDeepSeekAPI(apiKey, resumeText);
      return this.parsePersonalInfo(response);
    } catch (error) {
      console.error('Error extracting personal info:', error);
      return this.fallbackPersonalInfo(resumeText);
    }
  }

  async callDeepSeekAPI(apiKey, resumeText) {
    const prompt = `Extract personal information from this resume and return ONLY a JSON object with these fields:
{
  "firstName": "",
  "lastName": "", 
  "email": "",
  "phone": "",
  "location": "",
  "linkedin": "",
  "currentCompany": "",
  "currentPosition": "",
  "yearsExperience": "",
  "education": "",
  "skills": []
}

Resume:
${resumeText}`;

    const response = await fetch('https://api.deepseek.com/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 500,
        temperature: 0.3
      })
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data.choices[0].message.content;
  }

  parsePersonalInfo(response) {
    try {
      // Extract JSON from response
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      throw new Error('No JSON found in response');
    } catch (error) {
      console.error('Error parsing AI response:', error);
      return this.fallbackPersonalInfo(response);
    }
  }

  fallbackPersonalInfo(resumeText) {
    // Simple regex-based extraction as fallback
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
    const phoneRegex = /(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})/;
    
    return {
      firstName: '',
      lastName: '',
      email: resumeText.match(emailRegex)?.[0] || '',
      phone: resumeText.match(phoneRegex)?.[0] || '',
      location: '',
      linkedin: '',
      currentCompany: '',
      currentPosition: '',
      yearsExperience: '',
      education: '',
      skills: []
    };
  }

  async extractJobInformation() {
    const jobInfo = this.scrapeJobDetails();
    this.showNotification('Job information extracted', 'success');
    
    // Send to popup if open
    chrome.runtime.sendMessage({
      action: 'jobInfo',
      data: jobInfo
    });
  }

  scrapeJobDetails() {
    let jobInfo = {
      title: '',
      company: '',
      location: '',
      description: '',
      requirements: [],
      platform: this.currentPlatform
    };

    if (this.currentPlatform === 'linkedin') {
      jobInfo.title = document.querySelector('.jobs-unified-top-card__job-title')?.textContent?.trim() || '';
      jobInfo.company = document.querySelector('.jobs-unified-top-card__company-name')?.textContent?.trim() || '';
      jobInfo.location = document.querySelector('.jobs-unified-top-card__bullet')?.textContent?.trim() || '';
      jobInfo.description = document.querySelector('.jobs-box__html-content')?.textContent?.trim() || '';
    } else {
      // Generic scraping
      jobInfo.title = document.querySelector('h1, .job-title, .position-title')?.textContent?.trim() || '';
      jobInfo.company = document.querySelector('.company-name, .employer')?.textContent?.trim() || '';
      jobInfo.location = document.querySelector('.location, .job-location')?.textContent?.trim() || '';
    }

    return jobInfo;
  }

  async generateCoverLetter() {
    const jobInfo = this.scrapeJobDetails();
    if (!this.resumeData || !jobInfo.title) {
      this.showNotification('Please ensure both resume data and job information are available', 'error');
      return;
    }

    try {
      const apiKey = await this.getStoredApiKey();
      const coverLetter = await this.generateCoverLetterWithAI(apiKey, this.resumeData, jobInfo);
      
      // Try to fill cover letter field
      const coverLetterFields = document.querySelectorAll(this.fieldSelectors.coverLetter);
      if (coverLetterFields.length > 0) {
        coverLetterFields[0].value = coverLetter;
        coverLetterFields[0].dispatchEvent(new Event('input', { bubbles: true }));
        this.showNotification('Cover letter generated and inserted', 'success');
      } else {
        this.showCoverLetterModal(coverLetter);
      }
    } catch (error) {
      console.error('Error generating cover letter:', error);
      this.showNotification('Failed to generate cover letter', 'error');
    }
  }

  async generateCoverLetterWithAI(apiKey, resumeData, jobInfo) {
    const prompt = `Write a professional cover letter for this job application:

Job Title: ${jobInfo.title}
Company: ${jobInfo.company}
Location: ${jobInfo.location}

Job Description: ${jobInfo.description}

My Background: ${resumeData}

Requirements:
- Professional but personable tone
- 3-4 paragraphs maximum
- Highlight relevant skills and experience
- Show enthusiasm for the role
- Include a clear call to action
- Keep under 300 words`;

    const response = await fetch('https://api.deepseek.com/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 600,
        temperature: 0.7
      })
    });

    const data = await response.json();
    return data.choices[0].message.content.trim();
  }

  showCoverLetterModal(coverLetter) {
    const modal = document.createElement('div');
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.5);
      z-index: 10002;
      display: flex;
      align-items: center;
      justify-content: center;
    `;

    const content = document.createElement('div');
    content.style.cssText = `
      background: white;
      padding: 20px;
      border-radius: 8px;
      max-width: 600px;
      max-height: 80vh;
      overflow-y: auto;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;

    content.innerHTML = `
      <h3 style="margin-top: 0;">Generated Cover Letter</h3>
      <textarea style="width: 100%; height: 300px; margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">${coverLetter}</textarea>
      <div style="display: flex; gap: 10px; justify-content: flex-end;">
        <button id="copyCoverLetter" style="padding: 8px 16px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer;">Copy</button>
        <button id="closeCoverLetter" style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">Close</button>
      </div>
    `;

    modal.appendChild(content);
    document.body.appendChild(modal);

    // Event listeners
    content.querySelector('#copyCoverLetter').addEventListener('click', () => {
      navigator.clipboard.writeText(coverLetter);
      this.showNotification('Cover letter copied to clipboard', 'success');
    });

    content.querySelector('#closeCoverLetter').addEventListener('click', () => {
      modal.remove();
    });

    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.remove();
    });
  }

  observeDOMChanges() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
          // Check if new form fields were added
          const hasNewFormFields = Array.from(mutation.addedNodes).some(node => {
            return node.nodeType === 1 && (
              node.matches && node.matches('input, textarea, select') ||
              node.querySelector && node.querySelector('input, textarea, select')
            );
          });

          if (hasNewFormFields) {
            // Update field selectors for new content
            setTimeout(() => {
              this.fieldSelectors = this.getFieldSelectors();
            }, 500);
          }
        }
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  async loadSettings() {
    try {
      const result = await chrome.storage.sync.get(['autoFillEnabled', 'resumeData', 'deepseekApiKey']);
      this.isEnabled = result.autoFillEnabled || false;
      this.resumeData = result.resumeData || null;
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  }

  async getStoredApiKey() {
    try {
      const result = await chrome.storage.sync.get(['deepseekApiKey']);
      return result.deepseekApiKey;
    } catch (error) {
      console.error('Error getting API key:', error);
      return null;
    }
  }

  handleMessage(request, sender, sendResponse) {
    switch (request.action) {
      case 'fillFields':
        this.fillApplicationFields();
        sendResponse({ success: true });
        break;
      case 'analyzeFields':
        this.analyzeCurrentFields();
        sendResponse({ success: true });
        break;
      case 'extractJobInfo':
        const jobInfo = this.extractJobInformation();
        sendResponse({ success: true, data: jobInfo });
        break;
      case 'generateCoverLetter':
        this.generateCoverLetter();
        sendResponse({ success: true });
        break;
      case 'updateSettings':
        this.isEnabled = request.settings.autoFillEnabled;
        this.resumeData = request.settings.resumeData;
        sendResponse({ success: true });
        break;
    }
  }

  showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.getElementById('assistant-notification');
    if (existing) existing.remove();

    const notification = document.createElement('div');
    notification.id = 'assistant-notification';
    notification.textContent = message;

    const colors = {
      success: '#4CAF50',
      error: '#f44336',
      warning: '#ff9800',
      info: '#2196F3'
    };

    notification.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: ${colors[type] || colors.info};
      color: white;
      padding: 12px 20px;
      border-radius: 4px;
      z-index: 10003;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      animation: slideDown 0.3s ease-out;
    `;

    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideDown {
        from { transform: translateX(-50%) translateY(-100%); opacity: 0; }
        to { transform: translateX(-50%) translateY(0); opacity: 1; }
      }
    `;
    document.head.appendChild(style);

    document.body.appendChild(notification);

    // Auto-hide after 3 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.animation = 'slideDown 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
      }
    }, 3000);
  }
}

// Initialize the assistant when the page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new JobPortalAssistant();
  });
} else {
  new JobPortalAssistant();
}