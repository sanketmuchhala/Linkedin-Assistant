# LinkedIn Job Application Assistant

A powerful Chrome extension that uses AI to automatically fill job application forms on LinkedIn and other job portals.

## Features

- 🤖 **AI-Powered Form Filling**: Uses DeepSeek AI to intelligently map your resume to application forms
- 📋 **Smart Field Detection**: Automatically detects and fills common form fields
- 🔍 **Multi-Platform Support**: Works with LinkedIn, Simplify, JobRightAI, and generic job sites
- 💼 **Cover Letter Generation**: AI-generated cover letters tailored to specific jobs
- 📊 **Job Information Extraction**: Automatically extracts job details from postings
- ⚙️ **Privacy Focused**: All data stored locally, API calls only for AI processing

## Supported Platforms

- ✅ **LinkedIn Jobs** - Full support for all application forms
- ✅ **Simplify** - Comprehensive form filling
- ✅ **JobRightAI** - Complete integration
- ✅ **Generic Job Sites** - Basic form detection and filling

## Installation

1. **Download/Clone** this extension folder
2. **Open Chrome** and go to `chrome://extensions/`
3. **Enable Developer Mode** (toggle in top right)
4. **Click "Load unpacked"** and select the `extension` folder
5. **Pin the extension** to your browser toolbar

## Setup

1. **Click the extension icon** in your browser toolbar
2. **Enter your DeepSeek API key**:
   - Get a free API key from [DeepSeek](https://platform.deepseek.com/)
   - Paste it in the configuration section
   - Click "Save Configuration"
3. **Add your resume**:
   - Paste your resume text in the Resume section
   - Click "Save Resume" (it will be processed by AI)
4. **Enable auto-fill** using the toggle switch

## Usage

### Quick Actions (Floating Button)
When you're on a job site, you'll see a floating 🤖 button:
- **🔍 Analyze Fields** - Scan the current page for fillable fields
- **🚀 Auto-Fill Form** - Automatically fill detected fields
- **📋 Extract Job Info** - Get job details from the posting
- **💼 Generate Cover Letter** - Create tailored cover letter
- **⚙️ Settings** - Open configuration popup

### Extension Popup
Click the extension icon for full controls:
- Configure API key and resume
- Preview your processed data
- Manual form filling options
- Export/import settings

## Field Mapping

The extension automatically maps your resume to these common fields:

| Field Type | Auto-Filled From |
|------------|------------------|
| First/Last Name | Resume contact info |
| Email | Resume contact info |
| Phone | Resume contact info |
| Location | Resume address |
| LinkedIn Profile | Resume links |
| Current Company | Latest work experience |
| Current Position | Latest job title |
| Experience Level | Calculated from work history |
| Cover Letter | AI-generated based on job |

## Privacy & Security

- ✅ **Local Storage**: All personal data stored locally in Chrome
- ✅ **API Calls**: Only sent to DeepSeek for AI processing
- ✅ **No Tracking**: No analytics or user tracking
- ✅ **No Data Sharing**: Your information never shared with third parties
- ✅ **Secure**: All API communications over HTTPS

## Troubleshooting

### Extension Not Working
- Ensure you're on a supported job site
- Check that the extension is enabled in Chrome
- Verify your DeepSeek API key is valid
- Refresh the page and try again

### Fields Not Filling
- Make sure you've added your resume data
- Try the "Analyze Fields" button first
- Some sites use dynamic forms that load slowly
- Manual filling may be needed for custom fields

### API Errors
- Verify your DeepSeek API key is correct
- Check your internet connection
- Ensure you have API credits remaining
- Try regenerating your API key

## Development

### File Structure
```
extension/
├── manifest.json       # Extension configuration
├── popup.html         # Extension popup interface
├── popup.js          # Popup logic and controls
├── content.js        # Page interaction and form filling
├── background.js     # Background processing and API calls
└── README.md         # This file
```

### Key Components

- **Content Script** (`content.js`): Injected into job sites, handles form detection and filling
- **Background Script** (`background.js`): Manages API calls, storage, and cross-tab communication
- **Popup** (`popup.html/js`): User interface for configuration and manual controls

### API Integration

The extension integrates with DeepSeek API for:
- Resume parsing and structured data extraction
- Cover letter generation
- Field mapping intelligence

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on different job sites
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Open an issue on GitHub
3. Make sure to include browser version and error details

---

**Note**: This extension requires a DeepSeek API key for AI features. The free tier includes generous usage limits for personal use.