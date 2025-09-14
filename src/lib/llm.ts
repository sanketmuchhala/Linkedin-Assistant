import { ConnectionRecord } from '@prisma/client'
import { GenerationOutput } from './validations'

interface LLMProvider {
  generateContent(record: ConnectionRecord): Promise<GenerationOutput>
}

class GeminiProvider implements LLMProvider {
  private apiKey: string
  private model: string

  constructor(apiKey: string, model = 'gemini-1.5-pro') {
    this.apiKey = apiKey
    this.model = model
  }

  async generateContent(record: ConnectionRecord): Promise<GenerationOutput> {
    const prompt = this.buildPrompt(record)

    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${this.model}:generateContent?key=${this.apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [{
          parts: [{ text: prompt }]
        }],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 1000,
        }
      })
    })

    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.statusText}`)
    }

    const data = await response.json()
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text

    if (!text) {
      throw new Error('No content generated from Gemini')
    }

    return this.parseGeneratedContent(text)
  }

  private buildPrompt(record: ConnectionRecord): string {
    return `You are a LinkedIn Connection Assistant. Generate a personalized connection request and acceptance message.

CONTEXT:
Name: ${record.fullName}
Role: ${record.role || 'Unknown'}
Company: ${record.company || 'Unknown'}
LinkedIn URL: ${record.linkedinUrl}
Source: ${record.source}
Why Connect: ${record.whyConnect}
Shared Topics: ${record.sharedTopics || '[]'}
Evidence: ${record.evidence || '[]'}
Tone: ${record.tone || 'professional'}
Don't Do: ${record.doNotDo || '[]'}
Goal: ${record.goal || 'informational_chat'}
CTA: ${record.cta || ''}
Tags: ${record.tags || '[]'}

REQUIREMENTS:
1. Connection note: ≤300 characters, personalized, mentions specific context
2. Acceptance message: ≤600 characters, warm follow-up for after they accept
3. Use the specified tone: ${record.tone || 'professional'}
4. Avoid anything in "Don't Do" list
5. Focus on the goal: ${record.goal || 'informational_chat'}

OUTPUT FORMAT (valid JSON only):
{
  "connection_note": {
    "text": "Your connection request message here",
    "char_count": 250
  },
  "accept_message": {
    "text": "Your acceptance follow-up message here",
    "char_count": 400
  }
}`
  }

  private parseGeneratedContent(text: string): GenerationOutput {
    try {
      // Extract JSON from response (in case there's extra text)
      const jsonMatch = text.match(/\{[\s\S]*\}/)
      if (!jsonMatch) {
        throw new Error('No JSON found in response')
      }

      const parsed = JSON.parse(jsonMatch[0])

      // Validate the structure
      if (!parsed.connection_note?.text || !parsed.accept_message?.text) {
        throw new Error('Invalid response structure')
      }

      // Ensure character counts are correct
      parsed.connection_note.char_count = parsed.connection_note.text.length
      parsed.accept_message.char_count = parsed.accept_message.text.length

      // Enforce limits
      if (parsed.connection_note.char_count > 300) {
        parsed.connection_note.text = parsed.connection_note.text.substring(0, 297) + '...'
        parsed.connection_note.char_count = 300
      }

      if (parsed.accept_message.char_count > 600) {
        parsed.accept_message.text = parsed.accept_message.text.substring(0, 597) + '...'
        parsed.accept_message.char_count = 600
      }

      return parsed
    } catch (error) {
      throw new Error(`Failed to parse LLM response: ${error}`)
    }
  }
}

class DeepSeekProvider implements LLMProvider {
  private apiKey: string
  private model: string

  constructor(apiKey: string, model = 'deepseek-chat') {
    this.apiKey = apiKey
    this.model = model
  }

  async generateContent(record: ConnectionRecord): Promise<GenerationOutput> {
    const prompt = this.buildPrompt(record)

    const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: this.model,
        messages: [
          { role: 'system', content: 'You are a LinkedIn Connection Assistant. Generate personalized connection requests and acceptance messages. Always respond with valid JSON only.' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.7,
        max_tokens: 1000,
      })
    })

    if (!response.ok) {
      throw new Error(`DeepSeek API error: ${response.statusText}`)
    }

    const data = await response.json()
    const text = data.choices?.[0]?.message?.content

    if (!text) {
      throw new Error('No content generated from DeepSeek')
    }

    return this.parseGeneratedContent(text)
  }

  private buildPrompt(record: ConnectionRecord): string {
    return `Generate a LinkedIn connection request and acceptance message for:

Name: ${record.fullName}
Role: ${record.role || 'Unknown'}
Company: ${record.company || 'Unknown'}
Why Connect: ${record.whyConnect}
Tone: ${record.tone || 'professional'}
Goal: ${record.goal || 'informational_chat'}

Requirements:
- Connection note: ≤300 characters
- Acceptance message: ≤600 characters
- Use ${record.tone || 'professional'} tone
- Focus on ${record.goal || 'informational_chat'}

Respond with valid JSON only:
{
  "connection_note": {"text": "...", "char_count": 0},
  "accept_message": {"text": "...", "char_count": 0}
}`
  }

  private parseGeneratedContent(text: string): GenerationOutput {
    try {
      const jsonMatch = text.match(/\{[\s\S]*\}/)
      if (!jsonMatch) {
        throw new Error('No JSON found in response')
      }

      const parsed = JSON.parse(jsonMatch[0])

      if (!parsed.connection_note?.text || !parsed.accept_message?.text) {
        throw new Error('Invalid response structure')
      }

      parsed.connection_note.char_count = parsed.connection_note.text.length
      parsed.accept_message.char_count = parsed.accept_message.text.length

      if (parsed.connection_note.char_count > 300) {
        parsed.connection_note.text = parsed.connection_note.text.substring(0, 297) + '...'
        parsed.connection_note.char_count = 300
      }

      if (parsed.accept_message.char_count > 600) {
        parsed.accept_message.text = parsed.accept_message.text.substring(0, 597) + '...'
        parsed.accept_message.char_count = 600
      }

      return parsed
    } catch (error) {
      throw new Error(`Failed to parse LLM response: ${error}`)
    }
  }
}

class OllamaProvider implements LLMProvider {
  private baseUrl: string
  private model: string

  constructor(model = 'llama3', baseUrl = 'http://localhost:11434') {
    this.model = model
    this.baseUrl = baseUrl
  }

  async generateContent(record: ConnectionRecord): Promise<GenerationOutput> {
    const prompt = this.buildPrompt(record)

    const response = await fetch(`${this.baseUrl}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: this.model,
        prompt,
        stream: false,
        options: {
          temperature: 0.7,
          num_predict: 1000,
        }
      })
    })

    if (!response.ok) {
      throw new Error(`Ollama API error: ${response.statusText}`)
    }

    const data = await response.json()
    const text = data.response

    if (!text) {
      throw new Error('No content generated from Ollama')
    }

    return this.parseGeneratedContent(text)
  }

  private buildPrompt(record: ConnectionRecord): string {
    return `You are a LinkedIn Connection Assistant. Generate a personalized connection request and acceptance message.

Person: ${record.fullName} (${record.role} at ${record.company})
Why Connect: ${record.whyConnect}
Tone: ${record.tone || 'professional'}
Goal: ${record.goal || 'informational_chat'}

Requirements:
- Connection note: ≤300 characters, personalized
- Acceptance message: ≤600 characters, warm follow-up
- Use ${record.tone || 'professional'} tone

Respond with valid JSON only:
{
  "connection_note": {"text": "Your message here", "char_count": 0},
  "accept_message": {"text": "Your follow-up here", "char_count": 0}
}`
  }

  private parseGeneratedContent(text: string): GenerationOutput {
    try {
      const jsonMatch = text.match(/\{[\s\S]*\}/)
      if (!jsonMatch) {
        throw new Error('No JSON found in response')
      }

      const parsed = JSON.parse(jsonMatch[0])

      if (!parsed.connection_note?.text || !parsed.accept_message?.text) {
        throw new Error('Invalid response structure')
      }

      parsed.connection_note.char_count = parsed.connection_note.text.length
      parsed.accept_message.char_count = parsed.accept_message.text.length

      if (parsed.connection_note.char_count > 300) {
        parsed.connection_note.text = parsed.connection_note.text.substring(0, 297) + '...'
        parsed.connection_note.char_count = 300
      }

      if (parsed.accept_message.char_count > 600) {
        parsed.accept_message.text = parsed.accept_message.text.substring(0, 597) + '...'
        parsed.accept_message.char_count = 600
      }

      return parsed
    } catch (error) {
      throw new Error(`Failed to parse LLM response: ${error}`)
    }
  }
}

export class LLMAdapter {
  private provider: LLMProvider

  constructor() {
    const providerType = process.env.LLM_PROVIDER || 'gemini'

    switch (providerType.toLowerCase()) {
      case 'gemini':
        if (!process.env.GEMINI_API_KEY) {
          throw new Error('GEMINI_API_KEY environment variable is required')
        }
        this.provider = new GeminiProvider(
          process.env.GEMINI_API_KEY,
          process.env.GEMINI_MODEL
        )
        break

      case 'deepseek':
        if (!process.env.DEEPSEEK_API_KEY) {
          throw new Error('DEEPSEEK_API_KEY environment variable is required')
        }
        this.provider = new DeepSeekProvider(
          process.env.DEEPSEEK_API_KEY,
          process.env.DEEPSEEK_MODEL
        )
        break

      case 'ollama':
        this.provider = new OllamaProvider(
          process.env.OLLAMA_MODEL,
          process.env.OLLAMA_BASE_URL
        )
        break

      default:
        throw new Error(`Unsupported LLM provider: ${providerType}`)
    }
  }

  async generateContent(record: ConnectionRecord): Promise<GenerationOutput> {
    return this.provider.generateContent(record)
  }
}