// Popup script for LinkedIn Job Application Assistant
class PopupController {
  constructor() {
    this.settings = {};
    this.currentTab = null;
    this.init();
  }

  async init() {
    // Load current settings
    await this.loadSettings();
    
    // Setup event listeners
    this.setupEventListeners();
    
    // Get current tab info
    await this.getCurrentTab();
    
    // Update UI
    this.updateUI();
  }

  async loadSettings() {
    try {
      const response = await chrome.runtime.sendMessage({ action: 'getSettings' });
      if (response.success) {
        this.settings = response.settings;
      }
    } catch (error) {
      console.error('Error loading settings:', error);
      this.showStatus('Error loading settings', 'error');
    }
  }

  async getCurrentTab() {
    try {
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
      this.currentTab = tabs[0];
    } catch (error) {
      console.error('Error getting current tab:', error);
    }
  }

  setupEventListeners() {
    // Configuration
    document.getElementById('saveConfig').addEventListener('click', () => this.saveConfiguration());
    document.getElementById('saveResume').addEventListener('click', () => this.saveResume());
    
    // Auto-fill controls
    document.getElementById('autoFillEnabled').addEventListener('change', (e) => {
      this.settings.autoFillEnabled = e.target.checked;
      this.saveSettings();
    });
    
    document.getElementById('analyzeFields').addEventListener('click', () => this.analyzeFields());
    document.getElementById('fillFields').addEventListener('click', () => this.fillFields());
    document.getElementById('previewData').addEventListener('click', () => this.previewData());
    
    // Quick actions
    document.getElementById('extractJobInfo').addEventListener('click', () => this.extractJobInfo());
    document.getElementById('generateCoverLetter').addEventListener('click', () => this.generateCoverLetter());

    // Listen for messages from content script
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      this.handleMessage(request, sender, sendResponse);
    });
  }

  updateUI() {
    // Update form fields with current settings
    document.getElementById('apiKey').value = this.settings.deepseekApiKey || '';
    document.getElementById('resumeText').value = this.settings.resumeData || '';
    document.getElementById('autoFillEnabled').checked = this.settings.autoFillEnabled || false;

    // Update status based on configuration
    this.updateConfigurationStatus();
    
    // Update platform detection
    this.updatePlatformInfo();
  }

  updateConfigurationStatus() {
    const hasApiKey = this.settings.deepseekApiKey && this.settings.deepseekApiKey.length > 0;
    const hasResume = this.settings.resumeData && this.settings.resumeData.length > 0;
    
    if (hasApiKey && hasResume) {
      this.showStatus('✅ Extension configured and ready', 'success');
    } else if (hasApiKey) {
      this.showStatus('⚠️ Add your resume to enable auto-fill', 'warning');
    } else {
      this.showStatus('⚠️ Configure your DeepSeek API key to get started', 'warning');
    }
  }

  updatePlatformInfo() {
    if (this.currentTab && this.currentTab.url) {
      const url = this.currentTab.url.toLowerCase();
      let platform = 'Unknown';
      let supported = false;

      if (url.includes('linkedin.com')) {
        platform = 'LinkedIn';
        supported = true;
      } else if (url.includes('simplify.jobs')) {
        platform = 'Simplify';
        supported = true;
      } else if (url.includes('jobrightai.com')) {
        platform = 'JobRightAI';
        supported = true;
      }

      // Add platform indicator to popup (you could add this to HTML)
      const statusEl = document.getElementById('status');
      if (supported) {
        statusEl.innerHTML += `<br><small>📍 Current platform: ${platform} (Supported)</small>`;
      } else {
        statusEl.innerHTML += `<br><small>📍 Current platform: ${platform} (Limited support)</small>`;
      }
    }
  }

  async saveConfiguration() {
    const apiKey = document.getElementById('apiKey').value.trim();
    
    if (!apiKey) {
      this.showStatus('Please enter your DeepSeek API key', 'error');
      return;
    }

    this.showStatus('Testing API key...', 'info');

    try {
      // Test API key
      const testResponse = await chrome.runtime.sendMessage({
        action: 'testApiKey',
        apiKey: apiKey
      });

      if (testResponse.success && testResponse.isValid) {
        this.settings.deepseekApiKey = apiKey;
        await this.saveSettings();
        this.showStatus('✅ API key saved and validated', 'success');
      } else {
        this.showStatus('❌ Invalid API key. Please check and try again.', 'error');
      }
    } catch (error) {
      console.error('Error testing API key:', error);
      this.showStatus('❌ Error testing API key', 'error');
    }
  }

  async saveResume() {
    const resumeText = document.getElementById('resumeText').value.trim();
    
    if (!resumeText) {
      this.showStatus('Please enter your resume content', 'error');
      return;
    }

    if (!this.settings.deepseekApiKey) {
      this.showStatus('Please configure your API key first', 'error');
      return;
    }

    this.showStatus('Processing resume data...', 'info');

    try {
      // Process resume with AI
      const processResponse = await chrome.runtime.sendMessage({
        action: 'processResume',
        resumeText: resumeText
      });

      if (processResponse.success) {
        this.settings.resumeData = resumeText;
        this.settings.processedResumeData = processResponse.data;
        await this.saveSettings();
        this.showStatus('✅ Resume saved and processed', 'success');
      } else {
        throw new Error('Failed to process resume');
      }
    } catch (error) {
      console.error('Error processing resume:', error);
      // Save raw text even if processing fails
      this.settings.resumeData = resumeText;
      await this.saveSettings();
      this.showStatus('⚠️ Resume saved (processing failed)', 'warning');
    }
  }

  async saveSettings() {
    try {
      await chrome.runtime.sendMessage({
        action: 'saveSettings',
        settings: this.settings
      });
    } catch (error) {
      console.error('Error saving settings:', error);
      this.showStatus('Error saving settings', 'error');
    }
  }

  async analyzeFields() {
    if (!this.currentTab) {
      this.showStatus('No active tab detected', 'error');
      return;
    }

    this.showStatus('Analyzing form fields...', 'info');

    try {
      const response = await chrome.tabs.sendMessage(this.currentTab.id, {
        action: 'analyzeFields'
      });

      if (response && response.success) {
        this.showStatus('✅ Field analysis complete - check console for details', 'success');
      } else {
        throw new Error('Analysis failed');
      }
    } catch (error) {
      console.error('Error analyzing fields:', error);
      this.showStatus('❌ Could not analyze fields - make sure you\'re on a job application page', 'error');
    }
  }

  async fillFields() {
    if (!this.settings.resumeData) {
      this.showStatus('Please add your resume data first', 'error');
      return;
    }

    if (!this.currentTab) {
      this.showStatus('No active tab detected', 'error');
      return;
    }

    this.showStatus('Auto-filling form fields...', 'info');

    try {
      const response = await chrome.tabs.sendMessage(this.currentTab.id, {
        action: 'fillFields'
      });

      if (response && response.success) {
        this.showStatus('✅ Fields filled successfully', 'success');
        
        // Log analytics
        chrome.runtime.sendMessage({
          action: 'logAnalytics',
          event: {
            type: 'auto_fill',
            platform: this.detectCurrentPlatform(),
            url: this.currentTab.url
          }
        });
      } else {
        throw new Error('Fill fields failed');
      }
    } catch (error) {
      console.error('Error filling fields:', error);
      this.showStatus('❌ Could not fill fields - make sure you\'re on a job application form', 'error');
    }
  }

  async previewData() {
    if (!this.settings.processedResumeData && !this.settings.resumeData) {
      this.showStatus('No resume data available to preview', 'error');
      return;
    }

    // Create preview modal
    this.showDataPreview();
  }

  showDataPreview() {
    const modal = document.createElement('div');
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.5);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
    `;

    const content = document.createElement('div');
    content.style.cssText = `
      background: white;
      padding: 20px;
      border-radius: 8px;
      max-width: 90%;
      max-height: 80%;
      overflow-y: auto;
    `;

    const data = this.settings.processedResumeData || { raw: this.settings.resumeData };
    
    content.innerHTML = `
      <h3 style="margin-top: 0;">Resume Data Preview</h3>
      <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; font-size: 11px; overflow: auto;">${JSON.stringify(data, null, 2)}</pre>
      <div style="margin-top: 15px; display: flex; gap: 10px; justify-content: flex-end;">
        <button id="exportData" style="padding: 8px 16px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer;">Export</button>
        <button id="closePreview" style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">Close</button>
      </div>
    `;

    modal.appendChild(content);
    document.body.appendChild(modal);

    // Event listeners
    content.querySelector('#exportData').addEventListener('click', () => {
      this.exportData();
    });

    content.querySelector('#closePreview').addEventListener('click', () => {
      modal.remove();
    });

    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.remove();
    });
  }

  async exportData() {
    try {
      const exportData = await chrome.runtime.sendMessage({ action: 'exportData' });
      if (exportData.success) {
        const blob = new Blob([JSON.stringify(exportData.data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `linkedin-assistant-backup-${new Date().getTime()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        this.showStatus('✅ Data exported successfully', 'success');
      }
    } catch (error) {
      console.error('Export error:', error);
      this.showStatus('❌ Export failed', 'error');
    }
  }

  async extractJobInfo() {
    if (!this.currentTab) {
      this.showStatus('No active tab detected', 'error');
      return;
    }

    this.showStatus('Extracting job information...', 'info');

    try {
      const response = await chrome.tabs.sendMessage(this.currentTab.id, {
        action: 'extractJobInfo'
      });

      if (response && response.success) {
        this.showStatus('✅ Job information extracted', 'success');
      } else {
        throw new Error('Extraction failed');
      }
    } catch (error) {
      console.error('Error extracting job info:', error);
      this.showStatus('❌ Could not extract job information', 'error');
    }
  }

  async generateCoverLetter() {
    if (!this.settings.resumeData) {
      this.showStatus('Please add your resume data first', 'error');
      return;
    }

    if (!this.currentTab) {
      this.showStatus('No active tab detected', 'error');
      return;
    }

    this.showStatus('Generating cover letter...', 'info');

    try {
      const response = await chrome.tabs.sendMessage(this.currentTab.id, {
        action: 'generateCoverLetter'
      });

      if (response && response.success) {
        this.showStatus('✅ Cover letter generated', 'success');
      } else {
        throw new Error('Generation failed');
      }
    } catch (error) {
      console.error('Error generating cover letter:', error);
      this.showStatus('❌ Could not generate cover letter', 'error');
    }
  }

  detectCurrentPlatform() {
    if (!this.currentTab || !this.currentTab.url) return 'unknown';
    
    const url = this.currentTab.url.toLowerCase();
    if (url.includes('linkedin.com')) return 'linkedin';
    if (url.includes('simplify.jobs')) return 'simplify';
    if (url.includes('jobrightai.com')) return 'jobrightai';
    return 'generic';
  }

  handleMessage(request, sender, sendResponse) {
    switch (request.action) {
      case 'fieldAnalysis':
        console.log('Field Analysis:', request.data);
        this.showStatus(`Found ${request.data.fieldsFound} fields on ${request.data.platform}`, 'info');
        break;
      case 'jobInfo':
        console.log('Job Info:', request.data);
        this.showStatus('Job information extracted', 'success');
        break;
      default:
        console.log('Unknown message:', request);
    }
  }

  showStatus(message, type = 'info') {
    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    statusEl.className = `status ${type}`;
    statusEl.classList.remove('hidden');

    // Auto-hide after 5 seconds for success/info messages
    if (type === 'success' || type === 'info') {
      setTimeout(() => {
        statusEl.classList.add('hidden');
      }, 5000);
    }
  }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new PopupController();
});