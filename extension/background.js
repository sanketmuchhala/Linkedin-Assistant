// Background script for LinkedIn Job Application Assistant
class BackgroundService {
  constructor() {
    this.initializeService();
  }

  initializeService() {
    // Handle extension installation
    chrome.runtime.onInstalled.addListener((details) => {
      this.handleInstallation(details);
    });

    // Handle messages from content scripts and popup
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      this.handleMessage(request, sender, sendResponse);
      return true; // Keep the message channel open for async responses
    });

    // Handle storage changes
    chrome.storage.onChanged.addListener((changes, namespace) => {
      this.handleStorageChanges(changes, namespace);
    });

    // Handle tab updates to inject content script if needed
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      this.handleTabUpdate(tabId, changeInfo, tab);
    });
  }

  handleInstallation(details) {
    if (details.reason === 'install') {
      // Set default settings on first install
      chrome.storage.sync.set({
        autoFillEnabled: false,
        resumeData: null,
        deepseekApiKey: null,
        lastUpdated: Date.now()
      });

      // Open welcome page or popup
      chrome.tabs.create({
        url: chrome.runtime.getURL('popup.html')
      });
    } else if (details.reason === 'update') {
      // Handle extension updates
      console.log('Extension updated to version:', chrome.runtime.getManifest().version);
    }
  }

  async handleMessage(request, sender, sendResponse) {
    try {
      switch (request.action) {
        case 'openPopup':
          await this.openPopup();
          sendResponse({ success: true });
          break;

        case 'saveSettings':
          await this.saveSettings(request.settings);
          await this.notifyContentScripts('settingsUpdated', request.settings);
          sendResponse({ success: true });
          break;

        case 'getSettings':
          const settings = await this.getSettings();
          sendResponse({ success: true, settings });
          break;

        case 'testApiKey':
          const isValid = await this.testDeepSeekApi(request.apiKey);
          sendResponse({ success: true, isValid });
          break;

        case 'processResume':
          const processedData = await this.processResumeData(request.resumeText);
          sendResponse({ success: true, data: processedData });
          break;

        case 'generateCoverLetter':
          const coverLetter = await this.generateCoverLetter(request.jobInfo, request.resumeData);
          sendResponse({ success: true, coverLetter });
          break;

        case 'logAnalytics':
          await this.logAnalyticsEvent(request.event);
          sendResponse({ success: true });
          break;

        case 'exportData':
          const exportData = await this.exportUserData();
          sendResponse({ success: true, data: exportData });
          break;

        case 'importData':
          await this.importUserData(request.data);
          sendResponse({ success: true });
          break;

        default:
          console.warn('Unknown action:', request.action);
          sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      console.error('Error handling message:', error);
      sendResponse({ success: false, error: error.message });
    }
  }

  handleStorageChanges(changes, namespace) {
    if (namespace === 'sync') {
      // Notify all tabs about setting changes
      for (const key in changes) {
        if (['autoFillEnabled', 'resumeData', 'deepseekApiKey'].includes(key)) {
          this.notifyContentScripts('settingsChanged', { [key]: changes[key].newValue });
        }
      }
    }
  }

  async handleTabUpdate(tabId, changeInfo, tab) {
    // Only process complete page loads on job sites
    if (changeInfo.status !== 'complete' || !tab.url) return;

    const jobSites = [
      'linkedin.com',
      'simplify.jobs',
      'jobrightai.com'
    ];

    const isJobSite = jobSites.some(site => tab.url.includes(site));
    
    if (isJobSite) {
      // Ensure content script is injected
      try {
        await chrome.scripting.executeScript({
          target: { tabId },
          files: ['content.js']
        });
      } catch (error) {
        // Content script might already be injected
        console.log('Content script injection skipped:', error.message);
      }
    }
  }

  async openPopup() {
    // Get current window to position popup
    const currentWindow = await chrome.windows.getCurrent();
    
    // Create popup window
    await chrome.windows.create({
      url: chrome.runtime.getURL('popup.html'),
      type: 'popup',
      width: 400,
      height: 600,
      left: currentWindow.left + currentWindow.width - 420,
      top: currentWindow.top + 50
    });
  }

  async saveSettings(settings) {
    await chrome.storage.sync.set({
      ...settings,
      lastUpdated: Date.now()
    });
  }

  async getSettings() {
    const result = await chrome.storage.sync.get([
      'autoFillEnabled',
      'resumeData',
      'deepseekApiKey',
      'lastUpdated'
    ]);

    return {
      autoFillEnabled: result.autoFillEnabled || false,
      resumeData: result.resumeData || null,
      deepseekApiKey: result.deepseekApiKey || null,
      lastUpdated: result.lastUpdated || Date.now()
    };
  }

  async testDeepSeekApi(apiKey) {
    if (!apiKey) return false;

    try {
      const response = await fetch('https://api.deepseek.com/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          model: 'deepseek-chat',
          messages: [{ role: 'user', content: 'Test connection' }],
          max_tokens: 10
        })
      });

      return response.ok;
    } catch (error) {
      console.error('API test failed:', error);
      return false;
    }
  }

  async processResumeData(resumeText) {
    if (!resumeText) return null;

    try {
      const settings = await this.getSettings();
      if (!settings.deepseekApiKey) {
        throw new Error('DeepSeek API key not configured');
      }

      const response = await fetch('https://api.deepseek.com/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${settings.deepseekApiKey}`
        },
        body: JSON.stringify({
          model: 'deepseek-chat',
          messages: [{
            role: 'user',
            content: `Extract and structure this resume data into JSON format:

${resumeText}

Return ONLY a JSON object with these fields:
{
  "personalInfo": {
    "firstName": "",
    "lastName": "",
    "email": "",
    "phone": "",
    "location": "",
    "linkedin": ""
  },
  "professional": {
    "summary": "",
    "currentPosition": "",
    "currentCompany": "",
    "yearsExperience": "",
    "skills": [],
    "industries": []
  },
  "education": [
    {
      "degree": "",
      "school": "",
      "year": ""
    }
  ],
  "experience": [
    {
      "title": "",
      "company": "",
      "duration": "",
      "description": ""
    }
  ]
}`
          }],
          max_tokens: 1000,
          temperature: 0.3
        })
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.statusText}`);
      }

      const data = await response.json();
      const content = data.choices[0].message.content;

      // Extract JSON from response
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }

      throw new Error('Invalid JSON in API response');

    } catch (error) {
      console.error('Error processing resume:', error);
      // Return basic structure if processing fails
      return this.extractBasicInfo(resumeText);
    }
  }

  extractBasicInfo(resumeText) {
    // Fallback extraction using regex
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
    const phoneRegex = /(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})/;
    const linkedinRegex = /(?:linkedin\.com\/in\/|linkedin\.com\/profile\/view\?id=)([a-zA-Z0-9\-_%]+)/;

    return {
      personalInfo: {
        firstName: '',
        lastName: '',
        email: resumeText.match(emailRegex)?.[0] || '',
        phone: resumeText.match(phoneRegex)?.[0] || '',
        location: '',
        linkedin: resumeText.match(linkedinRegex)?.[0] || ''
      },
      professional: {
        summary: '',
        currentPosition: '',
        currentCompany: '',
        yearsExperience: '',
        skills: [],
        industries: []
      },
      education: [],
      experience: []
    };
  }

  async generateCoverLetter(jobInfo, resumeData) {
    try {
      const settings = await this.getSettings();
      if (!settings.deepseekApiKey) {
        throw new Error('DeepSeek API key not configured');
      }

      const prompt = `Write a professional cover letter for this job application:

Job Details:
- Title: ${jobInfo.title}
- Company: ${jobInfo.company}
- Location: ${jobInfo.location}
- Description: ${jobInfo.description}

Candidate Background:
- Name: ${resumeData.personalInfo?.firstName} ${resumeData.personalInfo?.lastName}
- Current Role: ${resumeData.professional?.currentPosition}
- Current Company: ${resumeData.professional?.currentCompany}
- Skills: ${resumeData.professional?.skills?.join(', ')}
- Experience: ${resumeData.professional?.summary}

Requirements:
- Professional but personable tone
- 3-4 short paragraphs
- Highlight relevant skills matching the job
- Show genuine interest in the company
- Include a clear call to action
- Keep under 300 words
- Ready to copy-paste format`;

      const response = await fetch('https://api.deepseek.com/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${settings.deepseekApiKey}`
        },
        body: JSON.stringify({
          model: 'deepseek-chat',
          messages: [{ role: 'user', content: prompt }],
          max_tokens: 600,
          temperature: 0.7
        })
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.statusText}`);
      }

      const data = await response.json();
      return data.choices[0].message.content.trim();

    } catch (error) {
      console.error('Error generating cover letter:', error);
      throw error;
    }
  }

  async notifyContentScripts(action, data) {
    try {
      const tabs = await chrome.tabs.query({});
      
      for (const tab of tabs) {
        try {
          await chrome.tabs.sendMessage(tab.id, { action, data });
        } catch (error) {
          // Tab might not have content script or be accessible
          console.log(`Could not notify tab ${tab.id}:`, error.message);
        }
      }
    } catch (error) {
      console.error('Error notifying content scripts:', error);
    }
  }

  async logAnalyticsEvent(event) {
    try {
      // Store analytics locally (could be sent to external service)
      const analytics = await chrome.storage.local.get(['analytics']) || { analytics: [] };
      analytics.analytics = analytics.analytics || [];
      
      analytics.analytics.push({
        ...event,
        timestamp: Date.now(),
        url: event.url || 'unknown'
      });

      // Keep only last 1000 events
      if (analytics.analytics.length > 1000) {
        analytics.analytics = analytics.analytics.slice(-1000);
      }

      await chrome.storage.local.set(analytics);
    } catch (error) {
      console.error('Error logging analytics:', error);
    }
  }

  async exportUserData() {
    try {
      const syncData = await chrome.storage.sync.get();
      const localData = await chrome.storage.local.get();
      
      return {
        settings: syncData,
        analytics: localData.analytics || [],
        exportDate: new Date().toISOString(),
        version: chrome.runtime.getManifest().version
      };
    } catch (error) {
      console.error('Error exporting data:', error);
      throw error;
    }
  }

  async importUserData(data) {
    try {
      if (data.settings) {
        await chrome.storage.sync.set(data.settings);
      }
      
      if (data.analytics) {
        await chrome.storage.local.set({ analytics: data.analytics });
      }

      // Notify content scripts of settings change
      await this.notifyContentScripts('settingsUpdated', data.settings);
    } catch (error) {
      console.error('Error importing data:', error);
      throw error;
    }
  }
}

// Initialize the background service
const backgroundService = new BackgroundService();